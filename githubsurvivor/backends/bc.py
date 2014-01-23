"""
BC backend
"""

from __future__ import absolute_import

from github import Github
from jira.client import JIRA
from jira.exceptions import JIRAError
from mongoengine import *

from githubsurvivor import config
from githubsurvivor.models import User, Issue

from pprint import pprint

import iso8601
import itertools
import jsonpickle
import os
import re
import redis

MAX_ISSUE_RESULTS = 999

def create_user(gh_user, verbose):
    "Create a User from a `github.NamedUser`."
    if gh_user['login'] in config.GITHUB_IGNORE_LOGINS:
        return

    try:
        return User.objects.get(login=gh_user['login'])
    except User.DoesNotExist:
        user = User(login=gh_user['login'],
                    name=gh_user['name'],
                    avatar_url='//www.gravatar.com/avatar/%s?s=52' % gh_user['gravatar_id'],
                    assigned_issues_url='https://github.com/%s/issues/assigned/%s' % \
                        (config.GITHUB_REPO, gh_user['login']))
        if verbose and user: print 'created user: %s' % user.login
        return user.save()

def create_update_issue_from_pull(gh_pull, jira_id, number, verbose):
    "Create an Issue from a `github.Pull`."

    commenters = [ ]
    for commenter in gh_pull['commenters']:
        commenters.append(create_user(commenter, verbose))

    reviewers = [ ]
    for reviewer in gh_pull['reviewers']:
        reviewers.append(create_user(reviewer, verbose))

    testers = [ ]
    for tester in gh_pull['testers']:
        testers.append(create_user(tester, verbose))

    try:
        issue = Issue.objects.get(key=jira_id)

        if issue.state != gh_pull['state']:
            if verbose: print 'updating issue state to %s: JIRA %s, PR %s' % (gh_pull['state'], jira_id, number)

        issue.state      = gh_pull['state']
        issue.opened     = gh_pull['created_at']
        issue.closed     = gh_pull['merged_at']
        issue.url        = gh_pull['html_url']
        issue.assignee   = create_user(gh_pull['user'], verbose)
        issue.merger     = create_user(gh_pull['merged_by'], verbose)
        issue.commenters = commenters
        issue.reviewers  = reviewers
        issue.testers    = testers
        issue.save()

        return issue
    except Issue.DoesNotExist:
        issue = Issue(key        = jira_id,
                      title      = jira_id,
                      state      = gh_pull['state'],
                      opened     = gh_pull['created_at'],
                      closed     = gh_pull['merged_at'],
                      url        = gh_pull['html_url'],
                      assignee   = create_user(gh_pull['user'], verbose),
                      merger     = create_user(gh_pull['merged_by'], verbose),
                      commenters = commenters,
                      reviewers  = reviewers,
                      testers    = testers)
        if verbose: print 'created issue: JIRA %s, PR %s' % (jira_id, number)
        return issue.save()

def create_issue_from_jira(jira_issue, verbose):
    "Creates a `githubsurvivor.models.Issue` from a `jira.resources.Issue`."
    try:
        return Issue.objects.get(key=jira_issue.key)
    except Issue.DoesNotExist:
        fields = jira_issue.fields
        issue = Issue(key    = jira_issue.key,
                      title  = jira_issue.key,
                      state  = 'open',
                      opened = iso8601.parse_date(fields.created),
                      closed = None,
                      url    = jira_issue.self)
        if verbose: print 'created issue: %s' % issue.title
        return issue.save()

class Importer(object):
    def __init__(self):
        github_auth_token                     = config.GITHUB_OAUTH_TOKEN
        github_account_name, github_repo_name = config.GITHUB_REPO.split('/')
        github                                = Github(github_auth_token, timeout=100)
        github_account                        = github.get_user(github_account_name)
        self.github_repo                      = github_account.get_repo(github_repo_name)
        github_organisation                   = github.get_organization(config.GITHUB_ORGANISATION)
        self.github_team                      = github_organisation.get_team(int(config.GITHUB_TEAM_ID))

        jira_username     = config.JIRA_USERNAME
        jira_password     = config.JIRA_PASSWORD
        jira_server       = config.JIRA_SERVER
        self.jira_project = config.JIRA_PROJECT

        self.jira = JIRA(
                basic_auth = (jira_username, jira_password),
                options    = {'server': jira_server})

    def import_users(self, verbose=False):
        # not really needed
        return
        for gh_user in self._fetch_users():
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as user_file:
                    user_data = jsonpickle.decode(user_file.read())
            else:
                user_data = {
                    'login'       : gh_user.login,
                    'name'        : gh_user.name,
                    'gravatar_id' : gh_user.gravatar_id
                    }

                with open(cache_file, 'w') as user_file:
                    user_file.write(jsonpickle.encode(user_data))

            user = create_user(user_data, verbose)

    def import_issues(self, verbose=False):
        redis_conn = redis.from_url(config.REDISTOGO_URL)

        # use GitHub to determine closed issues
        pulls = self._fetch_pulls()

        for pull in pulls:
            cacheable_pull = redis_conn.get('github-pull-'+str(pull.number))

            if cacheable_pull:
                try:
                    cacheable_pull = jsonpickle.decode(cacheable_pull)
                except ValueError:
                    cacheable_pull = None

            if not cacheable_pull:
                if verbose: print 'loading github pull request %s' % pull.number
                comments = itertools.chain(pull.get_review_comments(), pull.get_issue_comments())
                # you don't get points for commenting, reviewing or merging
                # your own PRs
                commenter_logins = [ ]
                commenters       = [ ]
                reviewer_logins  = [ ]
                reviewers        = [ ]
                review_regex     = re.compile(':\+1:')
                tester_logins    = [ ]
                testers          = [ ]
                tester_regex     = re.compile(':green_heart:')

                for comment in comments:
                    if comment.user.login == pull.user.login:
                        continue

                    # TODO: Don't add to commenters for review and test comments
                    if comment.user.login not in commenter_logins:
                        commenter_logins.append(comment.user.login)
                        commenters.append({
                            'login'       : comment.user.login,
                            'name'        : comment.user.name,
                            'gravatar_id' : comment.user.gravatar_id
                            })

                    if comment.user.login not in reviewer_logins:
                        review_match = review_regex.search(comment.body)

                        if review_match:
                            reviewer_logins.append(comment.user.login)
                            reviewers.append({
                                'login'       : comment.user.login,
                                'name'        : comment.user.name,
                                'gravatar_id' : comment.user.gravatar_id
                                })

                    if comment.user.login not in tester_logins:
                        tester_match = tester_regex.search(comment.body)

                        if tester_match:
                            tester_logins.append(comment.user.login)
                            testers.append({
                                'login'       : comment.user.login,
                                'name'        : comment.user.name,
                                'gravatar_id' : comment.user.gravatar_id
                                })

                merged_by_cacheable_user = None

                try:
                    merged_by_cacheable_user = {
                            'login'       : pull.merged_by.login,
                            'name'        : pull.merged_by.name,
                            'gravatar_id' : pull.merged_by.gravatar_id
                            }
                except AttributeError:
                    pass

                # retrieve from github
                cacheable_pull = {
                        'title'      : pull.title,
                        'state'      : pull.state,
                        'created_at' : pull.created_at,
                        'merged_at'  : pull.merged_at,
                        'html_url'   : pull.html_url,
                        'merged'     : pull.merged,
                        'merged_by'  : merged_by_cacheable_user,
                        'commenters' : commenters,
                        'reviewers'  : reviewers,
                        'testers'    : testers,

                        'user': {
                            'login'       : pull.user.login,
                            'name'        : pull.user.name,
                            'gravatar_id' : pull.user.gravatar_id
                            },
                        }

                # write to redis
                redis_conn.set('github-pull-'+str(pull.number), jsonpickle.encode(cacheable_pull))

            regex = re.compile('((?:[A-Za-z]{1,})-(?:[0-9]{1,}))')
            match = regex.search(pull.title)

            if cacheable_pull['merged'] and match:
                jira_id = match.group(1)
                cacheable_jira = redis_conn.get('jira-'+jira_id)

                if cacheable_jira:
                    try:
                        cacheable_jira = jsonpickle.decode(cacheable_jira)
                    except ValueError:
                        cacheable_jira = None

                if not cacheable_jira:
                    # check if this JIRA is valid
                    try:
                        if verbose: print 'loading jira issue %s' % jira_id
                        jira_issue = self.jira.issue(jira_id)
                        cacheable_jira = {
                                'valid'       : True,
                                'project_key' : jira_issue.fields.project.key,
                                'labels'      : jira_issue.fields.labels
                                }
                    except JIRAError:
                        # issue does not exist
                        cacheable_jira = {
                                'valid'       : False,
                                'project_key' : None,
                                'labels'      : [ ]
                                }

                    # write JIRA details to redis cache
                    redis_conn.set('jira-'+jira_id, jsonpickle.encode(cacheable_jira))

                if cacheable_jira['valid'] and \
                        (cacheable_jira['project_key'] == config.JIRA_PROJECT
                        or 'support-quickwin' in cacheable_jira['labels']
                        or 'eng-quickwin' in cacheable_jira['labels']
                        or 'product-quickwin' in cacheable_jira['labels']):
                    issue = create_update_issue_from_pull(cacheable_pull, jira_id, pull.number, verbose)

        # use JIRA to determine open issues
        for issue in self._fetch_jira_issues():
            create_issue_from_jira(issue, verbose)

    def _fetch_users(self):
        members = self.github_team.get_members()
        return members

    def _fetch_pulls(self):
        pulls = self.github_repo.get_pulls("closed")[:int(config.GITHUB_PULL_COUNT)]
        return pulls

    def _fetch_jira_issues(self):
        return itertools.chain(
                self.jira.search_issues(
                    'project=%s and status not in (Resolved, Closed, Triage)' % self.jira_project,
                    maxResults = MAX_ISSUE_RESULTS),
                self.jira.search_issues(
                    'labels in (support-quickwin, eng-quickwin, product-quickwin) and status not in (Resolved, Closed, Triage)',
                    maxResults = MAX_ISSUE_RESULTS))

def issue_importer():
    return Importer()
