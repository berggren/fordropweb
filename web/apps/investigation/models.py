from django.db import models
from django.contrib.auth.models import User
from apps.pages.models import Page

class ReferencePollManager(models.Manager):
    def get_count(self, reference):
        from apps.report.models import UserReport, UserFile
        reference_object = Reference.objects.get(name=reference)
        self.files = UserFile.objects.filter(reference=reference_object).count()
        self.reports = UserReport.objects.filter(reference=reference_object).count()
        self.result = self.files + self.reports
        return self.result

class Investigation(models.Model):
    title = models.CharField(max_length=255)
    description = models.ForeignKey(Page, null=True, blank=True, related_name="description")
    status = models.ForeignKey('Status', null=True, blank=True)
    creator = models.ForeignKey(User, null=True, blank=True, related_name="creator")
    investigator = models.ManyToManyField(User, null=True, blank=True, related_name="investigator")
    watcher = models.ManyToManyField(User, null=True, blank=True)
    reference = models.ManyToManyField('Reference', null=True, blank=True)
    pages = models.ManyToManyField(Page, null=True, blank=True, related_name="pages")
    graphid = models.IntegerField(null=True)
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

class Status(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % (self.name)
    class Admin:
        pass
