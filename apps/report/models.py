from django.db import models
from django.contrib.auth.models import User
from apps.investigation.models import *

class Report(models.Model):
    type = models.ForeignKey('TypeReport')
    value = models.TextField(null=True)
    md5 = models.CharField(max_length=255)
    sha1 = models.CharField(max_length=255)
    sha256 = models.CharField(max_length=255)
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % (self.value)
    class Admin:
        pass
    
class UserReport(models.Model):
    user = models.ForeignKey(User)
    report = models.ForeignKey(Report)
    reference = models.ForeignKey(Reference, null=True, blank=True)
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % (self.user)
    class Admin:
        pass

class TypeReport(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % (self.name)
    class Admin:
        pass