from django.contrib import admin
from apps.userprofile.models import UserProfile, UserSettings

admin.site.register(UserProfile)
admin.site.register(UserSettings)
