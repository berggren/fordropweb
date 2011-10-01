from django.db import models
from django.contrib.auth.models import User
from web.apps.pages.models import Page

class Investigation(models.Model):
    title = models.CharField(max_length=255)
    description = models.ForeignKey(Page, null=True, blank=True, related_name="description")
    status = models.CharField(max_length=255, null=True, blank=True)
    creator = models.ForeignKey(User, null=True, blank=True, related_name="creator")
    investigator = models.ManyToManyField(User, null=True, blank=True, related_name="investigator")
    reference = models.ManyToManyField('Reference', null=True, blank=True)
    pages = models.ManyToManyField(Page, null=True, blank=True, related_name="pages")
    graph_id = models.IntegerField(null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % self.title
    class Admin:
        pass

class Reference(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(User)
    time_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % self.name
    class Admin:
        pass