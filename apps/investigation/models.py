from django.db import models
from django.contrib.auth.models import User

class PollManager(models.Manager):
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
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % (self.title)
    class Admin:
        pass

class Reference(models.Model):
    name = models.CharField(max_length=255)
    investigation = models.ManyToManyField(Investigation)
    objects = PollManager()
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return '%s' % (self.name)
    class Admin:
        pass