import json
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from django.db import models
import hashlib
from taggit.managers import TaggableManager
from django.db.models.fields.files import ImageField
from fordrop.client import FordropRestClient
import uuid

xmpp = FordropRestClient(url=settings.FORDROP_PUBSUB_URL, username=settings.FORDROP_PUBSUB_USER, api_key=settings.FORDROP_PUBSUB_KEY, verify=settings.FORDROP_VERIFY_SSL)

class File(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    uuid = models.CharField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    filename = models.CharField(max_length=255, null=True, blank=True)
    filesize = models.IntegerField(null=True, blank=True)
    md5 = models.CharField(max_length=255, null=True, blank=True)
    sha1 = models.CharField(max_length=255, null=True, blank=True)
    sha256 = models.CharField(max_length=255, null=True, blank=True)
    sha512 = models.CharField(max_length=255, null=True, blank=True)
    ctph = models.CharField(max_length=255, null=True, blank=True)
    tags = TaggableManager(blank=True)
    nodes = models.ManyToManyField('PubSubNode', null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    def activity_object(self):
        return {
                    "hash": {
                        "md5": self.md5,
                        "sha1": self.sha1,
                        "sha256": self.sha256,
                        "sha512": self.sha512,
                        },
                    "id": self.uuid,
                    "description": self.description,
                    "objectType": "fordropFile"
                }
    def activity_fordrop_file(self):
        return {
            "verb": "post",
            "actor": self.user.profile.activity(),
            "object": self.activity_object(),
            "published": self.time_created.isoformat()
        }
    def activity_tags(self):
        def tags():
            l = []
            for tag in self.tags.all():
                l.append({
                    "objectType": "fordropTag",
                    "displayName": tag.name
                })
            return l
        target = self.activity_object()
        target['tags'] = tags()
        return {
                    "verb": "tag",
                    "actor": self.user.profile.activity(),
                    "target": target,
                    "published": self.time_created.isoformat()
                }
    def comments(self):
        return FileComment.objects.filter(file=self)
    def get_last_comment(self):
        return FileComment.objects.filter(file=self).order_by('-time_created')[0]
    def collections(self):
        return Collection.objects.filter(tags__in=self.tags.all).distinct()
    def get_reporters(self):
        return File.objects.filter(sha1=self.sha1).distinct()
    def __unicode__(self):
        return '%s' % self.sha1
    class Admin:
        pass

class Collection(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, related_name="user")
    followers = models.ManyToManyField(User, null=True, blank=True, related_name="followers")
    uuid = models.CharField(max_length=255, unique=True, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    tags = TaggableManager(blank=True)
    nodes = models.ManyToManyField('PubSubNode', null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    def comments(self):
        return CollectionComment.objects.filter(collection=self)
    def files(self):
        return File.objects.filter(tags__in=self.tags.all).distinct()
    def latest_file(self):
        try:
            return File.objects.filter(tags__in=self.tags.all).order_by('-time_created')[0]
        except IndexError:
            return None
    def get_absolute_url(self):
        return "/collection/%i" % self.id
    def timeline(self):
        files = File.objects.filter(tags__in=self.tags.all).distinct()
        l = []
        for file in files:
            link = "/file/%i" % file.id
            description = "Reported by: %s" % file.user.get_full_name()
            title = file.sha1
            l.append({'start': file.time_created.strftime('%Y-%m-%d %H:%M:%S'), 'title': title, 'link': link, 'description': description, 'color': 'orange'})
            for comment in file.comments():
                description = comment.content
                title = "Comment by: %s" % comment.user.profile.name
                l.append({'start': comment.time_created.strftime('%Y-%m-%d %H:%M:%S'), 'title': title, 'description': description, 'color': 'green'})
        for comment in self.comments():
            description = comment.content
            title = "Comment by: %s" % comment.user.profile.name
            l.append({'start': comment.time_created.strftime('%Y-%m-%d %H:%M:%S'), 'title': title, 'description': description, 'color': 'green'})
        j = {
            'dateTimeFormat': 'iso8601',
            'events' : l
        }
        return json.dumps(j)
    def activity_object(self):
        return {
                    "objectType": "fordropCollection",
                    "displayName": self.title,
                    "id": self.uuid,
                    "description": self.description,
                    "actor": self.user.profile.activity()
                    }
    def activity_fordrop_collection(self):
        return {
                    "verb": "post",
                    "object": self.activity_object(),
                    "published": self.time_created.isoformat()
                }
    def activity_tags(self):
        def tags():
            l = []
            for tag in self.tags.all():
                l.append({
                    "objectType": "fordropTag",
                    "displayName": tag.name
                })
            return l
        target = self.activity_object()
        target['tags'] = tags()
        return {
            "verb": "tag",
            "actor": self.user.profile.activity(),
            "target": target,
            "published": self.time_created.isoformat()
        }
    def activity_follow(self):
        return {
            "verb": "follow",
            "actor": self.user.profile.activity(),
            "object": self.activity_object(),
            "published": self.time_created.isoformat()
        }
    def activity_unfollow(self):
        return {
            "verb": "stop-following",
            "actor": self.user.profile.activity(),
            "object": self.activity_object(),
            "published": self.time_created.isoformat()
        }

    def __unicode__(self):
        return '%s' % self.title
    class Admin:
        pass

class FileComment(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    file = models.ForeignKey(File, null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    def activity(self):
        return {
                    "verb": "comment",
                    "author": self.user.profile.activity(),
                    "content": self.content,
                    "id": self.uuid,
                    "inReplyTo": self.file.activity_object(),
                    "published": self.time_created.isoformat()

                }
    def __unicode__(self):
        return '%s' % self.content
    class Admin:
        pass

class CollectionComment(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    collection = models.ForeignKey(Collection, null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    def activity(self):
        return {
                    "verb": "comment",
                    "author": self.user.profile.activity(),
                    "content": self.content,
                    "id": self.uuid,
                    "inReplyTo": self.collection.activity_object(),
                    "published": self.time_created.isoformat()

                }
    def __unicode__(self):
        return '%s' % self.content
    class Admin:
        pass

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    avatar = ImageField(upload_to='avatars', null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    web = models.URLField(null=True, blank=True)
    bio = models.TextField(max_length=140, null=True, blank=True)
    is_first_login = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    def activity(self):
        return {
            "objectType" : "person",
            "id": self.uuid,
            "displayName": self.name
        }
    def __unicode__(self):
        return '%s' % self.user
    def get_absolute_url(self):
        return '/profile/%s' % self.id
    def save(self, *args, **kwargs):
        super(UserProfile, self).save()
        if not self.uuid:
            self.uuid = uuid.uuid4().urn
            super(UserProfile, self).save()
    class Admin:
        pass

class UserSettings(models.Model):
    user = models.ForeignKey(User)
    notify_comment_on_file = models.BooleanField(default=False)
    notify_comment_on_collection = models.BooleanField(default=False)
    notify_same_file = models.BooleanField(default=False)
    publish_avatar = models.BooleanField(default=False)
    post_as_self = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % self.user
    class Admin:
        pass

class PubSubNode(models.Model):
    node = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=False)
    time_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % self.name
    class Admin:
        pass

def handle_uploaded_file(f):
    _file = f.read()
    md5 = hashlib.md5(_file).hexdigest()
    sha1 = hashlib.sha1(_file).hexdigest()
    sha256 = hashlib.sha256(_file).hexdigest()
    sha512 = hashlib.sha512(_file).hexdigest()
    result = {
        'filesize': f.size,
        'filename': f.name,
        'md5': md5,
        'sha1': sha1,
        'sha256': sha256,
        'sha512': sha512,
    }
    return result

def notify_by_mail(users=None, subject=None, body=None, obj=None):
    mails_to_send = []
    for user in users:
        if user == obj.user:
                continue
        if isinstance(obj, CollectionComment):
            if not user.settings.notify_comment_on_collection:
                continue
        if isinstance(obj, FileComment):
            if not user.settings.notify_comment_on_file:
                continue
        if isinstance(obj, File):
            if not user.settings.notify_same_file:
                continue
        mails_to_send.append((subject, body, settings.EMAIL_FROM_ADDR, [user.profile.email]))
    if not mails_to_send:
        return
    send_mass_mail(mails_to_send, fail_silently=False)

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
User.settings = property(lambda u: UserSettings.objects.get_or_create(user=u)[0])