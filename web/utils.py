from apps.report.models import *
from django.contrib.comments.models import *
from web.apps.investigation.models import Investigation

def activity_stream():
    stream = []
    comments = Comment.objects.all().order_by('-submit_date')[:10]
    files = UserFile.objects.all().order_by('-timecreated')[:10]
    reports = UserReport.objects.all().order_by('-timecreated')[:10]
    investigations = Investigation.objects.all().order_by('-timecreated')[:10]
    for comment in comments:
        stream.append({'type': 'comment', 'time': comment.submit_date, 'object': comment})
    for file in files:
        stream.append({'type': 'file', 'time': file.timecreated, 'object': file})
    for report in reports:
        stream.append({'type': 'report', 'time': report.timecreated, 'object': report})
    for investigation in investigations:
        stream.append({'type': 'investigation', 'time': investigation.timecreated, 'object': investigation})
    return stream

