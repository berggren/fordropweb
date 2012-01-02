from django.http import HttpResponse
from apps.investigation.models import Investigation
from apps.report.models import File
import graphutils as gc
import json

def timeline(request, investigation_id):
    investigation = Investigation.objects.get(pk=investigation_id)
    l = []
    tag_list = [x.name for x in investigation.tags.all()]
    files = File.objects.filter(tags__name__in=tag_list).distinct()
    for file in files:
        link = "/file/%i/show" % file.id
        description = "Reported by: %s<br>Filesize: %s<br>Type: %s" % (file.user.profile.name, file.filesize, file.filetype)
        title = "File added by %s: %s" % (file.user.profile.name, file.filename)
        d = {'start': file.time_created.strftime('%Y-%m-%d %H:%M:%S'), 'title': title, 'link': link, 'description': description, 'color': 'orange'}
        l.append(d)
    for post in investigation.posts.all():
        description = post.post
        title = "Comment by: %s" % post.author.profile.name
        d = {'start': post.time_created.strftime('%Y-%m-%d %H:%M:%S'), 'title': title, 'description': description, 'color': 'green'}
        l.append(d)
    j = {
            'dateTimeFormat': 'iso8601',
            'events' : l
        }
    j2 = json.dumps(j)
    return HttpResponse(j2)

def arbor(request):
    return gc.arbor(gc.neo4jdb, request.GET['n'])
