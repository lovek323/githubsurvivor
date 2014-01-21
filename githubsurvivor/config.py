from os import path

from derpconf.config import Config as c, verify_config, generate_config

# Core options

c.define('BACKEND',
         'github',
         'Specify issue-tracking backend')

c.define('DB',
         'githubsurvivor',
         'Mongo database to use as local datastore')

c.define('FLASK_DEBUG',
         False,
         'Whether to display the interactive debugger on error. Don\'t enable this in publicly-accessible environments.')

c.define('FLASK_SETTINGS',
         {'host': '127.0.0.1', 'port': 5000},
         'Options to pass to Flask initialiser')

# GitHub options

c.define('GITHUB_REPO',
         None,
         'Specify the GitHub repo you want to report on',
         'GitHub')

c.define('GITHUB_ORGANISATION',
        None,
        'Specify the GitHub organisation containing your team',
        'GitHub')

c.define('GITHUB_TEAM_ID',
        None,
        'Specify the GitHub team ID from which you wish to list users',
        'GitHub')

c.define('GITHUB_OAUTH_TOKEN',
         None,
         'OAuth token for accessing your repo. See https://help.github.com/articles/creating-an-oauth-token-for-command-line-use',
         'GitHub')

c.define('GITHUB_IGNORE_LOGINS',
        [ ],
        'Logins to ignore',
        'GitHub')

c.define('GITHUB_PULL_COUNT',
        1000,
        'Number of pull requests to fetch from GitHub',
        'GitHub')

# JIRA options

c.define('JIRA_SERVER',
         None,
         'JIRA server URL',
         'JIRA')

c.define('JIRA_USERNAME',
         None,
         'Authorised JIRA username',
         'JIRA')

c.define('JIRA_PASSWORD',
         None,
         'JIRA account password',
         'JIRA')

c.define('JIRA_PROJECT',
         None,
         'JIRA project key',
         'JIRA')

c.define('JIRA_FILTER_ID',
        None,
        'JIRA filter ID',
        'JIRA')

# Reporting options

c.define('LEADERBOARD_USERS',
         [],
         'Optional list of users to display in the bug leaderboards. Leave this empty to include all repo contributors.',
         'Reporting')

c.define('REPORTING_WINDOW',
         'month',
         'Size of reporting window; one of week, sprint, month',
         'Reporting')

c.define('REPORTING_SPRINT_START_WEEKDAY',
         'monday',
         'Day of week starting a sprint-based reporting window',
         'Reporting')

c.define('REPORTING_SPRINT_LENGTH_WEEKS',
         2,
         'Length of sprint-based reporting window',
         'Reporting')

c.define('REPORTING_FIRST_SPRINT_WEEK_OF_YEAR',
         1,
         'Week of year in which the first sprint begins',
         'Reporting')

# API

class Config(object):

    DEFAULT_FILENAME = 'githubsurvivor.conf'
    SEARCH_DIRS = [path.curdir,
                   path.expanduser('~'),
                   '/etc']

    def load(self, config_path=None):
        """
        Load configuration from file. If no config path is given, several
        directories are searched for a file named 'githubsurvivor.conf': the
        current directory, followed by the current user's home directory, then
        finally /etc.
        """
        if not config_path:
            config_path = c.get_conf_file(self.DEFAULT_FILENAME, self.SEARCH_DIRS)

        if not config_path:
            raise Exception(
                'No configuration provided, and none found at any of %s' % \
                    ', '.join(path.join(d, self.DEFAULT_FILENAME) for d in self.SEARCH_DIRS))

        self._config = c.load(config_path or self._default_path())

    def __getattr__(self, key):
        if not self._config: raise Exception('Not initialised')
        return getattr(self._config, key)

def generate():
    generate_config()
