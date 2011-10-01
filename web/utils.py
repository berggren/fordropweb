from apps.report.models import *
from django.contrib.comments.models import *
from web.apps.investigation.models import Investigation

def activity_stream():
    stream = []
    comments = Comment.objects.all().order_by('-submit_date')[:10]
    files = UserFile.objects.all().order_by('-time_created')[:10]
    investigations = Investigation.objects.all().order_by('-time_created')[:10]
    for comment in comments:
        stream.append({'type': 'comment', 'time': comment.submit_date, 'object': comment})
    for file in files:
        stream.append({'type': 'file', 'time': file.time_created, 'object': file})
    for investigation in investigations:
        stream.append({'type': 'investigation', 'time': investigation.time_created, 'object': investigation})
    return stream

def investigation_activity_stream(id):
    stream = []
    files = []
    investigation = Investigation.objects.get(pk=id)
    comments = Comment.objects.for_model(Investigation).filter(object_pk=investigation.id)
    for ref in investigation.reference.all():
        ref_files = UserFile.objects.filter(reference=ref)
        for file in ref_files:
            if file not in files:
                files.append(file)
    for comment in comments:
        stream.append({'type': 'comment', 'time': comment.submit_date, 'object': comment})
    for file in files:
        stream.append({'type': 'file', 'time': file.timecreated, 'object': file})
    return stream

