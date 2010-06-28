from django.db import models
from django.contrib.auth.models import User
from tagging.models import *

TYPE_CHOICES = (
    ('M', 'Mail'),
    ('U', 'Url'),
)

class Phishing(models.Model):
    md5 = models.CharField(max_length=255)
    sha1 = models.CharField(max_length=255)
    sha256 = models.CharField(max_length=255)
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % (self.sha1)
    class Admin:
        pass
    
class UserPhishing(models.Model):
    user = models.ForeignKey(User)
    phish = models.ForeignKey(Phishing)
    reference = models.ForeignKey(Tag, null=True, blank=True)
    data = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES)
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % (unicode(self.phish))
    class Admin:
        pass
