from django.contrib.contenttypes import generic
from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from apps.post.models import Post

class File(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    filename = models.CharField(max_length=255, null=True, blank=True)
    filesize = models.IntegerField(null=True, blank=True)
    filetype = models.CharField(max_length=255, null=True, blank=True)
    datefolder = models.CharField(max_length=255, null=True, blank=True)
    md5 = models.CharField(max_length=255, null=True, blank=True)
    sha1 = models.CharField(max_length=255, null=True, blank=True)
    sha256 = models.CharField(max_length=255, null=True, blank=True)
    graph_id = models.IntegerField(null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    published = models.BooleanField()
    tags = TaggableManager()
    posts = generic.GenericRelation(Post)
    time_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    @models.permalink
    def get_absolute_url(self):
        return ('apps.report.views.file', [str(self.id)])
    def __unicode__(self):
        return '%s' % self.sha1
    class Admin:
        pass

class MalwareMhr(models.Model):
    file = models.ForeignKey(File)
    percent = models.IntegerField(null=True)
    timecreated_mhr = models.DateTimeField(null=True)
    donotexist = models.BooleanField()
    time_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % self.file
    class Admin:
        pass
