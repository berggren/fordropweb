from apps.report.models import File
from django.contrib.comments.models import *
from apps.investigation.models import Investigation
from apps.post.models import NewPost

def activity_stream():
    stream = []
    files = File.objects.all().order_by('-time_created')[:10]
    posts = NewPost.objects.all().order_by('-time_created')[:10]
    investigations = Investigation.objects.all().order_by('-time_created')[:10]
    for file in files:
        stream.append({'type': 'file', 'time': file.time_created, 'object': file})
    for post in posts:
        stream.append({'type': 'post', 'time': post.time_created, 'object': post})
    for investigation in investigations:
        stream.append({'type': 'investigation', 'time': investigation.time_created, 'object': investigation})
    return stream

def investigation_activity_stream(id):
    investigation = Investigation.objects.get(pk=id)
    stream = []
    tag_list = [x.name for x in investigation.tags.all()]
    files = File.objects.filter(tags__name__in=tag_list).distinct()[:10]
    posts = NewPost.objects.filter(investigation=investigation).order_by('-time_created')[:10]
    for file in files:
        stream.append({'type': 'file', 'time': file.time_created, 'object': file})
    for post in posts:
        stream.append({'type': 'post', 'time': post.time_created, 'object': post})
    return stream

def user_activity_stream(id):
    stream = []
    user = User.objects.get(pk=id)
    files = File.objects.filter(user=user).order_by('-time_created')[:10]
    posts = NewPost.objects.filter(user=user).order_by('-time_created')[:10]
    for file in files:
        stream.append({'type': 'file', 'time': file.time_created, 'object': file})
    for post in posts:
        stream.append({'type': 'post', 'time': post.time_created, 'object': post})
    return stream
