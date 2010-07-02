from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from apps.search.forms import *
from apps.upload.models import *
from apps.report.models import *
from apps.investigation.models import *
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
    report_tags = Tag.objects.cloud_for_model(Report,  steps=5, distribution=LOGARITHMIC, filters=None, min_count=None)
    tagcloud = files_tags + report_tags
    stream = activity_stream()
    return render_to_response('index.html', {'stream': stream, 'searchform': searchform, 'files': files, 'comments': comments, 'tagcloud': tagcloud}, RequestContext(request))

@login_required
def add_tag(request, obj_type, obj_id):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            _tag = form.cleaned_data['tag']
            if obj_type == "file":
                _object = File.objects.get(id=obj_id)
            if obj_type == "report":
                _object = Report.objects.get(id=obj_id)
            Tag.objects.add_tag(_object, _tag)
    return HttpResponseRedirect(request.META["HTTP_REFERER"])

@login_required
def add_reference(request, obj_type, obj_id):
    if request.method == 'POST':
        form = ReferenceForm(request.POST)
        if form.is_valid():
            _ref_name = form.cleaned_data['reference']
            print _ref_name
            _ref_object, created = Reference.objects.get_or_create(name=_ref_name)
            if obj_type == "file":
                _object = UserFile.objects.get(id=obj_id)
            if obj_type == "report":
                _object = UserReport.objects.get(id=obj_id)
            _object.reference = _ref_object
            _object.save()
    return HttpResponseRedirect(request.META["HTTP_REFERER"])

def timeline(request):
    l = []
    for file in UserFile.objects.all():
        link = "/file/%i/show" % file.file.id
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