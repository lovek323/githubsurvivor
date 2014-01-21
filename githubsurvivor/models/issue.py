from mongoengine import *
from mongoengine.queryset import QuerySet

from githubsurvivor.models import User

class IssueQuerySet(QuerySet):
    """
    Custom issue queries.
    """
    def opened_in(self, start, end):
        "Find issues opened in date range."
        return self.filter(opened__gt=start, opened__lte=end)

    def older_than(self, date):
        "Find open issues created before a given date."
        return self.filter(opened__lt=date, state='open')

    def closed_in(self, start, end):
        "Find issues closed in date range."
        return self.filter(closed__gt=start, closed__lte=end)

    def open_at(self, time):
        "Find open issues at a point in time."
        return self.filter(opened__lt=time, closed__not__lt=time)

    def unassigned(self):
        "Find unassigned open issues."
        return self.filter(state='open', assignee=None)

class Issue(Document):
    """
    Some bug that may or may not have been fixed.
    """
    meta = {'queryset_class': IssueQuerySet}

    key = StringField(required=True)
    title = StringField(required=True)
    state = StringField(required=True) # {open, closed}
    opened = DateTimeField(required=True)
    closed = DateTimeField()
    url = StringField()

    assignee = ReferenceField(User, dbref=False)
    commenters = ListField(ReferenceField(User, dbref=False))
    reviewers = ListField(ReferenceField(User, dbref=False))
    merger = ReferenceField(User, dbref=False)
