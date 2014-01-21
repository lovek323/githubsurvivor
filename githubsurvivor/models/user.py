from mongoengine import *
from mongoengine.queryset import QuerySet

from githubsurvivor import config

class UserQuerySet(QuerySet):
    """
    Custom user queries.
    """
    def developers(self):
        "Return all those users that should be included in the leaderboard."
        whitelist = config.LEADERBOARD_USERS
        return [u for u in self.all() if not whitelist or u.login in whitelist]

class User(Document):
    """
    Some developer that fixes bugs.
    """
    meta = {'queryset_class': UserQuerySet}

    login = StringField(required=True)
    avatar_url = StringField()
    assigned_issues_url = StringField()

    def assigned_issues(self):
        return self.issues().filter(state='open')

    def closed_issues(self):
        from githubsurvivor.models import Issue
        return Issue.objects(assignee=self).filter(state='closed')

    def commented_issues(self):
        from githubsurvivor.models import Issue
        return Issue.objects(commenters__contains=self).filter(state='closed')

    def reviewed_issues(self):
        from githubsurvivor.models import Issue
        return Issue.objects(reviewers__contains=self).filter(state='closed')

    def merged_issues(self):
        from githubsurvivor.models import Issue
        return Issue.objects(merger=self).filter(state='closed')
