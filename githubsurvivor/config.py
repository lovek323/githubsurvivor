import os

class Config(object):
    CONFIG_OPTIONS = [
            'BACKEND',
            'FLASK_DEBUG',
            'GITHUB_IGNORE_LOGINS',
            'GITHUB_OAUTH_TOKEN',
            'GITHUB_ORGANISATION',
            'GITHUB_PULL_COUNT',
            'GITHUB_REPO',
            'GITHUB_TEAM_ID',
            'JIRA_FILTER_ID',
            'JIRA_PASSWORD',
            'JIRA_PROJECT',
            'JIRA_SERVER',
            'JIRA_USERNAME',
            'LEADERBOARD_USERS',
            'MONGOHQ_URL',
            'REDISTOGO_URL',
            'REPORTING_SPRINT_LENGTH_WEEKS',
            'REPORTING_SPRINT_START_WEEKDAY',
            'REPORTING_SPRINT_WEEK_OF_YEAR',
            'REPORTING_WINDOW',
            ]

    BACKEND = 'bc'
    FLASK_DEBUG = True
    FLASK_SETTINGS = None
    GITHUB_IGNORE_LOGINS = [ ]
    GITHUB_OAUTH_TOKEN = None
    GITHUB_ORGANISATION = None
    GITHUB_PULL_COUNT = 100
    GITHUB_REPO = None
    GITHUB_TEAM_ID = None
    JIRA_FILTER_ID = None
    JIRA_PASSWORD = None
    JIRA_PROJECT = None
    JIRA_SERVER = None
    JIRA_USERNAME = None
    LEADERBOARD_USERS = [ ]
    MONGOHQ_URL = 'mongodb://127.0.0.1/githubsurvivor'
    REDISTOGO_URL = 'redis://localhost:6379'
    REPORTING_SPRINT_LENGTH_WEEKS = None
    REPORTING_SPRINT_START_WEEKDAY = None
    REPORTING_SPRINT_WEEK_OF_YEAR = None
    REPORTING_WINDOW = 'week'

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
