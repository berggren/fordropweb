import json
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from web.apps.investigation.models import Investigation, Reference
from web.apps.report.models import UserFile, File
from web.apps.report.forms import UploadFileForm
import web.graphutils as gc
from web.utils import investigation_activity_stream
from uuid import uuid4

print gc.neo4jdb

def get_people(investigation):
    """
    List of active people in a investigation, based on references
    """
    people = [investigation.creator]
    for ref in investigation.reference.all():
        ref_files = UserFile.objects.filter(reference=ref)
        for file in ref_files:
            if file.user == investigation.creator:
                continue
            if file.user not in people:
                people.append(file.user)
    return people

@login_required
def create(request):
    """
    Create a new investigation
    """
    if request.method == 'POST':
        title = request.POST['title']
        investigation, created = Investigation.objects.get_or_create(title=title, creator=request.user)
        if created:
            investigation.uuid = uuid4().urn
        investigation.investigator.add(request.user)
        investigation.save()
        url = "/investigation/%i" % investigation.id
        gc.add_node(request, investigation, "investigation")
        gc.add_relationship(investigation.creator.get_profile().graph_id, investigation.graph_id, "created")
        mail_body = "A new investigation were created by %s" % investigation.creator.get_full_name()
        send_mail('New investigation: %s' % investigation.title,
                                            mail_body,
                                            'fordrop@django',
                                            ['jbn@django'],
                                            fail_silently=True)
        return HttpResponseRedirect(url)

@login_required
def overview(request, id):
    """
    Dashboard of a investigation
    """
    investigation = Investigation.objects.get(pk=id)
    people = get_people(investigation)
    upload_form = UploadFileForm()
    stream = investigation_activity_stream(investigation.id)
    files = []
    for ref in investigation.reference.all():
        f = UserFile.objects.filter(reference=ref)
        for file in f:
            files.append(file)
    return render_to_response('investigation/overview.html',
                                                                {
                                                                    'investigation': investigation,
                                                                    'uploadform': upload_form,
                                                                    'stream': stream,
                                                                    'people': people,
                                                                    'files': files,
                                                                }, RequestContext(request))

@login_required
def wiki(request, id):
    """
    Simple wiki like system
    """
    investigation = Investigation.objects.get(pk=id)
    people = get_people(investigation)
    return render_to_response('investigation/wiki.html',
                                                            {
                                                                'investigation': investigation,
                                                                'people': people
                                                            }, RequestContext(request))

@login_required
def timeline(request, id):
    """
    Timeline of investigation
    """
    investigation = Investigation.objects.get(pk=id)
    people = get_people(investigation)
    files = []
    for ref in investigation.reference.all():
        f = UserFile.objects.filter(reference=ref)
        for file in f:
            files.append(file)
    start_date = investigation.time_created.strftime('%Y %m %d %H:%M:%S')
    return render_to_response('investigation/timeline.html',
                                                                {
                                                                    'investigation': investigation,
                                                                    'startdate': start_date,
                                                                    'files': files,
                                                                    'people': people
                                                                }, RequestContext(request))

@login_required
def library(request, id):
    """
    Objects in a investigation
    """
    investigation = Investigation.objects.get(pk=id)
    people = get_people(investigation)
    files = []
    for ref in investigation.reference.all():
        ref_files = UserFile.objects.filter(reference=ref)
        for file in ref_files:
            if file not in files:
                files.append(file)
    return render_to_response('investigation/library.html',
                                                                {
                                                                    'investigation': investigation,
                                                                    'files': files,
                                                                    'people': people
                                                                }, RequestContext(request))

@login_required
def graph(request, id):
    """
    Visualization, objects in the graph with the investigation node as reference_node in neo4j
    Implemented with arbor.js, see the javascript in the template
    """
    investigation = Investigation.objects.get(pk=id)
    return render_to_response('investigation/graph.html',
                                                            {
                                                                'investigation': investigation
                                                            }, RequestContext(request))

@login_required
def related(request, id):
    investigation = Investigation.objects.get(id=id)
    related = json.loads(gc.get_related2(gc.neo4jdb, investigation.graph_id))['nodes']
    people = []
    investigations = []
    files = []
    for k,v  in related.items():
        if v['web_id']:
            if v['type'] == 'person':
                people.append(User.objects.get(pk=v['web_id']))
            if v['type'] == 'investigation':
                investigations.append(Investigation.objects.get(pk=v['web_id']))
            if v['type'] == 'report':
                files.append(File.objects.get(pk=v['web_id']))
    print related
    return render_to_response('investigation/related.html',
                                                            {
                                                                'investigation': investigation,
                                                                'people':           people,
                                                                'investigations':   investigations,
                                                                'files':            files,
                                                            }, RequestContext(request))

@login_required
def add_reference(request, id):
    """
    Add reference to investigation
    """
    investigation = Investigation.objects.get(id=id)
    if request.method == "POST":
        reference, created = Reference.objects.get_or_create(name=request.POST['reference'])
        reference.users.add(request.user)
        investigation.reference.add(reference)
    return HttpResponseRedirect(request.META["HTTP_REFERER"])