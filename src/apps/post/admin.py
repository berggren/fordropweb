from django.contrib import admin
from apps.post.models import Post, NewPost

admin.site.register(Post)
admin.site.register(NewPost)