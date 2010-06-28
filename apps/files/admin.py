from django.contrib import admin
from fordrop.apps.files.models import *

admin.site.register(File)
admin.site.register(UserFile)