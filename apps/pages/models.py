from django.db import models
from django.contrib.auth.models import User
import reversion

class Page(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    creator = models.ForeignKey(User, null=True, blank=True)
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % (self.title)
    class Admin:
        pass

reversion.register(Page)