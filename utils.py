from fordrop.apps.files.models import *
from fordrop.apps.phishing.models import *
from django.contrib.comments.models import *

def activity_stream():
    stream = []
    comments = Comment.objects.all().order_by('-submit_date')[:10]
    files = UserFile.objects.all().order_by('-timecreated')[:10]
    phishing = UserPhishing.objects.all().order_by('-timecreated')[:10]
    for comment in comments:
        stream.append({'type': 'comment', 'time': comment.submit_date, 'object': comment})
    for file in files:
        stream.append({'type': 'file', 'time': file.timecreated, 'object': file})
    for phish in phishing:
        stream.append({'type': 'phishing', 'time': phish.timecreated, 'object': phish})
    return stream