from django.contrib.contenttypes import generic
from django.db import models
from django.contrib.auth.models import User
from apps.pages.models import Page
from apps.post.models import Post
from taggit.managers import TaggableManager

class Investigation(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    creator = models.ForeignKey(User, null=True, blank=True, related_name="creator")
    investigator = models.ManyToManyField(User, null=True, blank=True, related_name="investigator")
    pages = models.ManyToManyField(Page, null=True, blank=True, related_name="pages")
    graph_id = models.IntegerField(null=True)
    posts = generic.GenericRelation(Post)
    uuid = models.CharField(max_length=255)
    tags = TaggableManager()
    time_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    @models.permalink
    def get_absolute_url(self):
        return ('apps.investigation.views.overview', [str(self.id)])
    def __unicode__(self):
        return '%s' % self.title
    class Admin:
        pass


