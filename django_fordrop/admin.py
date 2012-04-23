from django.contrib import admin
from models import File, FileComment, Collection, UserProfile, UserSettings, PubSubNode

admin.site.register(File)
admin.site.register(FileComment)
admin.site.register(Collection)
admin.site.register(UserProfile)
admin.site.register(UserSettings)
admin.site.register(PubSubNode)