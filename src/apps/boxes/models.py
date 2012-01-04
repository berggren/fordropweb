from django.db import models

class Box(models.Model):
    node = models.CharField(max_length=255, null=True, blank=True, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % self.name
    class Admin:
        pass
