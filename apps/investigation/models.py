from django.db import models
from django.contrib.auth.models import User
from fordrop.apps.news.models import News

class ReferencePollManager(models.Manager):
    def get_count(self, reference):
        from fordrop.apps.upload.models import UserFile
        from fordrop.apps.report.models import UserReport
        reference_object = Reference.objects.get(name=reference)
        self.files = UserFile.objects.filter(reference=reference_object).count()
        self.reports = UserReport.objects.filter(reference=reference_object).count()
        self.result = self.files + self.reports
        return self.result

class Investigation(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    investigator = models.ManyToManyField(User, null=True, blank=True, related_name="investigator")
    follower = models.ManyToManyField(User, null=True, blank=True)
    related_link = models.ManyToManyField(News, null=True, blank=True)
    reference = models.ManyToManyField('Reference', null=True, blank=True)
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % (self.title)
    class Admin:
        pass

class Reference(models.Model):
    name = models.CharField(max_length=255)
    objects = ReferencePollManager()
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % (self.name)
    class Admin:
        pass