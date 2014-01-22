import os

from githubsurvivor.tasks.sync import main

if not os.path.exists('tmp'):
    os.makedirs('tmp')

if not os.path.exists('tmp/github'):
    os.makedirs('tmp/github')

if not os.path.exists('tmp/github/users'):
    os.makedirs('tmp/github/users')

if not os.path.exists('tmp/github/pulls'):
    os.makedirs('tmp/github/pulls')

if not os.path.exists('tmp/jira'):
    os.makedirs('tmp/jira')

main()
