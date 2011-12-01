import json
from uuid import uuid4
from django.contrib.comments.models import Comment
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib.comments.signals import comment_was_posted
from sleekxmpp.xmlstream.jid import JID
from tagging.models import *
from fordrop import FordropXmpp
from xml.etree import cElementTree as ET
from web.apps.post.models import Post
from web.apps.investigation.models import *

class File(models.Model):
    filesize = models.IntegerField(null=True)
    filetype = models.CharField(max_length=255)
    datefolder = models.CharField(max_length=255)
    md5 = models.CharField(max_length=255)
    sha1 = models.CharField(max_length=255)
    sha256 = models.CharField(max_length=255)
    graph_id = models.IntegerField(null=True)
    uuid = models.CharField(max_length=255)
    time_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % self.sha1
    class Admin:
        pass
    
class UserFile(models.Model):
    user = models.ForeignKey(User)
    file = models.ForeignKey(File)
    filename = models.CharField(max_length=255)
    reference = models.ForeignKey(Reference, null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % (unicode(self.filename))
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

def publish(sender, **kwargs):
    item = ET.Element('event')
    if sender == Post or sender == File:
        if 'created' in kwargs:
            if kwargs['created']:
                obj = kwargs['instance']
            else:
                return
        else:
            return
    else:
        obj = kwargs['comment']
    act = make_activity(obj)
    item.text = json.dumps(act, indent=4)
    jid = JID('jbn@red.local')
    xmpp = FordropXmpp(jid, 'hej123')
    pubsub = xmpp['xep_0060']
    xmpp.run('192.168.56.101', threaded=True)
    pubsub.publish('pubsub.red.local', 'SUNET', payload=item)
    xmpp.disconnect()

def make_activity(obj):
        activity = {}
        published = '2011-02-10T15:04:55Z'
        object = {}
        target = None
        if isinstance(obj, File):
            actor = {'objectType':'organisation', 'displayName':'jbntest'}
            object['objectType'] = 'fordrop_file'
            object['hash'] = {'md5': obj.md5, 'sha1': obj.sha1, 'sha256': obj.sha256}
            object['id'] = obj.sha256
        elif isinstance(obj, Post):
            actor = {'objectType':'person', 'displayName':obj.author.username}
            object['objectType'] = 'fordrop_post'
            object['content'] = obj.post
            object['inReplyTo'] = {}
            object['id'] = obj.uuid
        elif isinstance(obj, Comment):
            actor = {'objectType':'person', 'displayName':obj.user.username}
            object['objectType'] = 'Comment'
            object['content'] = obj.comment
            object['id'] = uuid4().hex
            if isinstance(obj.content_object, File):
                object['inReplyTo'] = {'objectType': 'fordrop_file', 'id': obj.content_object.sha256}
        else:
            return None
        activity['published'] = published
        activity['verb'] = "post"
        activity['actor'] = actor
        activity['object'] = object
        if target:
            activity['target'] = target
        return activity

def make_person_object(user):
    return {'objectType': 'fordropPerson', 'displayName': user.username}

post_save.connect(publish, sender=File, dispatch_uid="file")
post_save.connect(publish, sender=Post, dispatch_uid="post")
comment_was_posted.connect(publish, sender=Comment, dispatch_uid="comment")