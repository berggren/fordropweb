from django.contrib.contenttypes import generic
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from taggit.managers import TaggableManager
from managers import PostManager
from apps.boxes.models import Box
from apps.investigation.models import Investigation
from apps.report.models import File

class Post(models.Model):
    author = models.ForeignKey(User, null=True, blank=True)
    post = models.TextField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    uuid = models.CharField(max_length=255)
    tags = TaggableManager(blank=True)
    boxes = models.ManyToManyField(Box, blank=True)
    published = models.BooleanField(default=True)
    objects = PostManager()
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s, %s' % (self.content_type, self.author)
    class Admin:
        pass

class NewPost(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    uuid = models.CharField(max_length=255)
    tags = TaggableManager(blank=True)
    boxes = models.ManyToManyField(Box, blank=True)
    published = models.BooleanField(default=True)
    file = models.ForeignKey(File, blank=True, null=True)
    investigation = models.ForeignKey(Investigation, blank=True, null=True)
    post = models.ForeignKey('self', blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % self.user
    class Admin:
        pass