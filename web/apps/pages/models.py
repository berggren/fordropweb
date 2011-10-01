from django.db import models
from django.contrib.auth.models import User

class Page(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    creator = models.ForeignKey(User, null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % self.title
    class Admin:
        pass
