from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from apps.search.forms import *
#from apps.report.models import *
#from apps.report.forms import *
from apps.report.forms import *
from apps.report.utils import *
from apps.pages.models import *
from apps.investigation.models import *
#from django.contrib.comments.models import *
from django.contrib.auth.decorators import login_required
#from tagging.models import *
#from tagging.utils import *
from forms import *
import simplejson
#import datetime
from utils import *
from django.contrib.contenttypes.models import ContentType
from apps.investigation.models import *

@login_required
def index(request):
    searchform = SearchForm()
    files = UserFile.objects.filter(user=request.user).order_by('-timecreated')
    stream = activity_stream()
    investigations = Investigation.objects.all()
    return render_to_response('apps/userprofile/dashboard.html', {'investigations': investigations, 'stream': stream, 'searchform': searchform, 'files': files, 'uploadform': UploadFileForm(), 'genericreportform': GenericReportForm()}, RequestContext(request))

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
            if obj_type == "page":
                _object = Page.objects.get(id=obj_id)
            if obj_type == "investigation":
                _object = Investigation.objects.get(id=obj_id)
            Tag.objects.add_tag(_object, _tag)
    return HttpResponseRedirect(request.META["HTTP_REFERER"])

@login_required
def add_reference(request, obj_type, obj_id):
    if request.method == 'POST':
        form = ReferenceForm(request.POST)
        if form.is_valid():
            _ref_name = form.cleaned_data['reference']
            _ref_object, created = Reference.objects.get_or_create(name=_ref_name)
            if obj_type == "file":
                _object = UserFile.objects.get(id=obj_id)
            if obj_type == "report":
                _object = UserReport.objects.get(id=obj_id)
            _object.reference = _ref_object
            _object.save()
            #ref_node = add_node_to_graph(_ref_object, "reference")
            #file_node = add_node_to_graph(_object, "file")
            #rel = add_relationship_to_graph(ref_node, file_node, "part of")

    return HttpResponseRedirect(request.META["HTTP_REFERER"])

def timeline(request, investigation_id):
    investigation = Investigation.objects.get(pk=investigation_id)
    investigation_type = ContentType.objects.get(model="investigation")
    l = []
    for ref in investigation.reference.all():
        files = UserFile.objects.filter(reference=ref)
        for file in files:
            link = "/file/%i/show" % file.file.id
            description = "Reported by: %s<br>Filesize: %s<br>Type: %s" % (file.user.get_full_name(), file.file.filesize, file.file.filetype)
            title = "File added by %s: %s" % (file.user.get_full_name(), file.filename)
            d = {'start': file.timecreated.strftime('%Y-%m-%d %H:%M:%S'), 'title': title, 'link': link, 'description': description, 'color': 'orange'}
            l.append(d)
    for comment in Comment.objects.filter(content_type=investigation_type, object_pk=investigation.id):
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