from django.contrib import admin
from fordrop.apps.upload.models import *

admin.site.register(File)
admin.site.register(UserFile)
admin.site.register(MalwareMhr)