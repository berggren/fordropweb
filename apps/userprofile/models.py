from django.db import models
from django.contrib.auth.models import User
from easy_thumbnails.fields import ThumbnailerImageField

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    avatar = ThumbnailerImageField(upload_to='avatars')
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % (self.user)
    class Admin:
        pass