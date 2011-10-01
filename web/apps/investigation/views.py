from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from web.apps.investigation.models import Investigation, Reference
from web.apps.pages.models import Page
from web.apps.report.models import UserFile
from web.apps.report.forms import UploadFileForm
from web.graphutils import FordropGraphClient
from web.utils import investigation_activity_stream

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
        description, created = Page.objects.get_or_create(title=title, creator=request.user, content=None)
        investigation, created = Investigation.objects.get_or_create(title=title,
                                                                     creator=request.user,
                                                                     description=description)
        investigation.pages.add(description)
        investigation.investigator.add(request.user)
        investigation.save()
        url = "/investigation/%i" % investigation.id
        gc = FordropGraphClient()
        gc.add_node(request, investigation, "investigation")
        gc.add_relationship(investigation.creator.get_profile().graphid, investigation.graphid, "created")
        send_mail('New investigation: %s' % investigation.title, 'A new investigation were created by %s' %
                                                                 investigation.creator.get_full_name(),
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
    return render_to_response('apps/investigation/overview.html',
                                                                {
                                                                    'investigation': investigation,
                                                                    'uploadform': upload_form,
                                                                    'stream': stream,
                                                                    'people': people
                                                                }, RequestContext(request))

@login_required
def wiki(request, id):
    """
    Simple wiki like system
    """
    investigation = Investigation.objects.get(pk=id)
    people = get_people(investigation)
    return render_to_response('apps/investigation/wiki.html',
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
    start_date = investigation.timecreated.strftime('%Y %m %d %H:%M:%S')
    return render_to_response('apps/investigation/timeline.html',
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
    return render_to_response('apps/investigation/library.html',
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
    return render_to_response('apps/investigation/graph.html',
                                                            {
                                                                'investigation': investigation
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