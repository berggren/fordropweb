from django.db import models
from django.contrib.auth.models import User
from apps.investigation.models import *
from tagging.models import *

class File(models.Model):
    filesize = models.IntegerField(null=True)
    filetype = models.CharField(max_length=255)
    datefolder = models.CharField(max_length=255)
    md5 = models.CharField(max_length=255)
    sha1 = models.CharField(max_length=255)
    sha256 = models.CharField(max_length=255)
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % (self.md5)
    class Admin:
        pass
    
class UserFile(models.Model):
    user = models.ForeignKey(User)
    file = models.ForeignKey(File)
    filename = models.CharField(max_length=255)
    reference = models.ForeignKey(Reference, null=True, blank=True)
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % (unicode(self.filename))
    class Admin:
        pass

class MalwareMhr(models.Model):
    file = models.ForeignKey(File)
    percent = models.IntegerField(null=True)
    timecreated_mhr = models.DateTimeField(null=True)
    donotexist = models.BooleanField()
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % (self.file)
    class Admin:
        pass

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