from django.db import models
from django.contrib.auth.models import User

class Investigation(models.Model):
    title = models.CharField(max_length=255)
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % (self.title)
    class Admin:
        pass

class Reference(models.Model):
    name = models.CharField(max_length=255)
    investigation = models.ManyToManyField(Investigation)
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % (self.name)
    class Admin:
        pass