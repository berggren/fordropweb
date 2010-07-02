from fordrop.apps.upload.models import *
from fordrop.apps.report.models import *
from django.contrib.comments.models import *

def activity_stream():
    stream = []
    comments = Comment.objects.all().order_by('-submit_date')[:10]
    files = UserFile.objects.all().order_by('-timecreated')[:10]
    reports = UserReport.objects.all().order_by('-timecreated')[:10]
    for comment in comments:
        stream.append({'type': 'comment', 'time': comment.submit_date, 'object': comment})
    for file in files:
        stream.append({'type': 'file', 'time': file.timecreated, 'object': file})
    for report in reports:
        stream.append({'type': 'report', 'time': report.timecreated, 'object': report})
    return stream