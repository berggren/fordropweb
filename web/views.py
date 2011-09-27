from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from apps.search.forms import *
from apps.report.forms import *
from django.contrib.auth.decorators import login_required
from forms import *
import simplejson
from utils import *
from django.contrib.contenttypes.models import ContentType
from apps.investigation.models import *
from graphutils import FordropGraphClient

@login_required
def add_tag(request, obj_type, obj_id):
    if request.method == 'POST':
        form = TagForm(request.POST)
        _object = None
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
def add_reference(request, type, id):
    if request.method == 'POST':
        ref_name = request.POST['reference']
        ref_object, created = Reference.objects.get_or_create(name=ref_name)
        ref_object.users.add(request.user)
        file = UserFile.objects.get(id=id)
        file.reference = ref_object
        file.save()
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

def arbor(request):
    graph = FordropGraphClient()
    return graph.gen_arbor_json(request.GET['n'])

def related(request):
    graph = FordropGraphClient()
    return graph.get_related(request.GET['n'])
