import mongoengine
import re

from pprint import pprint

from githubsurvivor.config import Config

def init_db(db_url):
    regex = re.compile('^mongodb:\\/\\/(.*?):(.*?)@(.*?):([0-9]+)\\/(.*)$')
    match = regex.match(db_url)

    if not match:
        regex = re.compile('^mongodb:\\/\\/(.*?)\\/(.*)$')
        match = regex.match(db_url)

        username = None
        password = None
        host = match.group(1)
        port = None
        db_name = match.group(2)
    else:
        username = match.group(1)
        password = match.group(2)
        host = match.group(3)
        port = int(match.group(4))
        db_name = match.group(5)

    print 'connecting: username = %s, password = %s, host = %s, port = %s, name = %s' % (username, password, host, port, db_name)

    conn = mongoengine.connect(db_name,
            host=host,
            port=port,
            username=username,
            password=password)

    return conn[db_name]

# Global configuration
config = Config()

# Database connection
db = None

def init():
    global db
    config.load()
    db = init_db(config.MONGOHQ_URL)
