from django.contrib.contenttypes import generic
from django.db import models
from django.contrib.auth.models import User
from tagging.models import Tag
from taggit.managers import TaggableManager
from apps.post.models import Post
from apps.pages.models import Page
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.boxes.models import Box

class File(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    filename = models.CharField(max_length=255, null=True, blank=True)
    filesize = models.IntegerField(null=True, blank=True)
    filetype = models.CharField(max_length=255, null=True, blank=True)
    datefolder = models.CharField(max_length=255, null=True, blank=True)
    md5 = models.CharField(max_length=255, null=True, blank=True)
    sha1 = models.CharField(max_length=255, null=True, blank=True)
    sha256 = models.CharField(max_length=255, null=True, blank=True)
    sha512 = models.CharField(max_length=255, null=True, blank=True)
    ctph = models.CharField(max_length=255, null=True, blank=True)
    graph_id = models.IntegerField(null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    published = models.BooleanField()
    tags = TaggableManager(blank=True)
    posts = generic.GenericRelation(Post)
    boxes = models.ManyToManyField(Box, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    @models.permalink
    def get_absolute_url(self):
        return 'apps.report.views.file', [str(self.id)]
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

@receiver(post_save, sender=Tag)
def my_handler(sender, **kwargs):
    print sender