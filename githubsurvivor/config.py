import os

class Config(object):
    CONFIG_OPTIONS = [
            'BACKEND',
            'MONGOHQ_URL',
            'FLASK_DEBUG',
            'GITHUB_REPO',
            'GITHUB_ORGANISATION',
            'GITHUB_TEAM_ID',
            'GITHUB_OAUTH_TOKEN',
            'GITHUB_IGNORE_LOGINS',
            'GITHUB_PULL_COUNT',
            'JIRA_SERVER',
            'JIRA_USERNAME',
            'JIRA_PASSWORD',
            'JIRA_PROJECT',
            'JIRA_FILTER_ID',
            'LEADERBOARD_USERS',
            'REPORTING_WINDOW',
            'REPORTING_SPRINT_START_WEEKDAY',
            'REPORTING_SPRINT_LENGTH_WEEKS',
            'REPORTING_SPRINT_WEEK_OF_YEAR',
            ]

    BACKEND = 'bc'
    MONGOHQ_URL = 'mongodb://127.0.0.1/githubsurvivor'
    FLASK_DEBUG = True
    FLASK_SETTINGS = None
    GITHUB_REPO = None
    GITHUB_ORGANISATION = None
    GITHUB_TEAM_ID = None
    GITHUB_OAUTH_TOKEN = None
    GITHUB_IGNORE_LOGINS = [ ]
    GITHUB_PULL_COUNT = None
    JIRA_SERVER = None
    JIRA_USERNAME = None
    JIRA_PASSWORD = None
    JIRA_PROJECT = None
    JIRA_FILTER_ID = None
    LEADERBOARD_USERS = [ ]
    REPORTING_WINDOW = 'week'
    REPORTING_SPRINT_START_WEEKDAY = None
    REPORTING_SPRINT_LENGTH_WEEKS = None
    REPORTING_SPRINT_WEEK_OF_YEAR = None

    def load(self):
        """
        Load configuration from environment.
        """

        for key in self.CONFIG_OPTIONS:
            if os.environ.get(key):
                setattr(self, key, os.environ.get(key))

        self.FLASK_SETTINGS = {'host': '0.0.0.0', 'port': int(os.environ.get('PORT'))}

    def __getattr__(self, key):
        if not self._config: raise Exception('Not initialised')
        return getattr(self._config, key)

def generate():
    generate_config()
