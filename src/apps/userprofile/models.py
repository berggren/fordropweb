import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from sorl.thumbnail import ImageField
import graphutils as gc

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, null=True, blank=True)
    is_first_login = models.BooleanField(default=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    avatar = ImageField(upload_to='avatars', null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    web = models.URLField(null=True, blank=True)
    bio = models.TextField(max_length=140, null=True, blank=True)
    graph_id = models.IntegerField(null=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % self.user
    class Admin:
        pass

class UserSettings(models.Model):
    user = models.ForeignKey(User)
    notification_new_follower = models.BooleanField(default=False)
    notification_comment_on_post = models.BooleanField(default=False)
    notification_same_file = models.BooleanField(default=False)
    notification_investigation_post = models.BooleanField(default=False)
    notification_investigation_file = models.BooleanField(default=False)
    notification_investigation_new_investigator = models.BooleanField(default=False)
    avatar_public = models.BooleanField(default=False)
    post_as_you = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % self.user
    class Admin:
        pass

def add_user_to_graph(sender, **kwargs):
    if 'created' in kwargs:
        obj = kwargs['instance']
        if kwargs['created']:
            gc.add_node(gc.neo4jdb, None, obj, 'person')
            if not obj.name:
                obj.name = obj.user.username
            if not obj.uuid:
                obj.uuid = uuid.uuid4().urn
            obj.save()
        else:
            #return
            gc.change_name_on_person_node(gc.neo4jdb, obj)
    else:
        return

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
User.settings = property(lambda u: UserSettings.objects.get_or_create(user=u)[0])
post_save.connect(add_user_to_graph, sender=UserProfile, dispatch_uid="userprofile")
