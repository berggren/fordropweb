from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from apps.search.forms import *
from apps.files.models import *
from apps.phishing.models import *
from django.contrib.comments.models import *
from django.contrib.auth.decorators import login_required
from tagging.models import *
from tagging.utils import *
from forms import *
import simplejson
import datetime
from utils import *

@login_required
def index(request):
    searchform = SearchForm()
    files = UserFile.objects.all().order_by('-timecreated')[:10]
    comments = Comment.objects.all().order_by('-submit_date')[:3]
    files_tags = Tag.objects.cloud_for_model(File,  steps=5, distribution=LOGARITHMIC, filters=None, min_count=None)
    phish_tags = Tag.objects.cloud_for_model(Phishing,  steps=5, distribution=LOGARITHMIC, filters=None, min_count=None)
    tagcloud = files_tags + phish_tags
    stream = activity_stream()
    return render_to_response('index.html', {'stream': stream, 'searchform': searchform, 'files': files, 'comments': comments, 'tagcloud': tagcloud}, RequestContext(request))

@login_required
def add_tag(request, obj_type, obj_id):
    ref_obj = None
    is_reference = False
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            _tag = form.cleaned_data['tag']
            try:
                if request.POST['ref']:
                    is_reference = True
            except: pass
            if obj_type == "file":
                _object = File.objects.get(id=obj_id)
                if is_reference:
                    ref_obj = UserFile.objects.get(user=request.user, file=_object)
            if obj_type == "phishing":
                _object = Phishing.objects.get(id=obj_id)
                if is_reference:
                    ref_obj = UserPhishing.objects.get(user=request.user, phish=_object)
            Tag.objects.add_tag(_object, _tag)
            if ref_obj:
                tag_obj = Tag.objects.get(name=_tag)
                ref_obj.reference = tag_obj
                ref_obj.save()
    return HttpResponseRedirect(request.META["HTTP_REFERER"])

def timeline(request):
    l = []
    for file in UserFile.objects.all():
        link = "/files/%i/show" % file.file.id
        description = "Reported by: %s<br>Filesize: %s<br>Type: %s" % (file.user.get_full_name(), file.file.filesize, file.file.filetype)
        title = "File added: %s" % file.filename
        d = {'start': file.timecreated.strftime('%Y-%m-%d %H:%M:%S'), 'title': title, 'link': link, 'description': description, 'color': 'orange'}
        l.append(d)

    for comment in Comment.objects.all():
        description = comment.comment
        title = "Comment by: %s" % comment.user.get_full_name()
        d = {'start': comment.submit_date.strftime('%Y-%m-%d %H:%M:%S'), 'title': title, 'description': description, 'color': 'green'}
        l.append(d)
    j = {
            'dateTimeFormat': 'iso8601',
            'events' : l
        }
    j2 = simplejson.dumps(j)
    return HttpResponse(j2) 