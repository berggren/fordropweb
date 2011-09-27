from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import *
from apps.search.forms import *
from apps.report.models import *
from apps.pages.models import *
from apps.report.utils import *
from django.contrib.auth.decorators import login_required
from utils import *
from forms import *

from web.graphutils import FordropGraphClient

# Reversion
#from reversion.models import Version
#from reversion import revision
#from web.apps.report.models import UserFile

def get_people(investigation):
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
    if request.method == 'POST':
        references = []
        for key, value in request.POST.iteritems():
            if "reference_" in key and value == "on":
                references.append(key.split("_")[1])
        title = request.POST['title']
        description, created = Page.objects.get_or_create(title=title   , creator=request.user, content=None)
        investigation, created = Investigation.objects.get_or_create(title=title, creator=request.user, description=description)
        investigation.pages.add(description)
        for ref in references:
            reference = Reference.objects.get(name=ref)
            investigation.reference.add(reference)
            investigation.save()
        url = "/investigation/%i" % investigation.id
        gc = FordropGraphClient()
        gc.add_node(request, investigation, "investigation")
        gc.add_relationship(investigation.creator.get_profile().graphid, investigation.graphid, "created")
        return HttpResponseRedirect(url)
    investigations = Investigation.objects.all()
    newinvestigationform = NewInvestigationForm()
    return render_to_response('apps/investigation/index.html', {'investigations': investigations, 'newinvestigationform': newinvestigationform}, RequestContext(request))

@login_required
#@revision.create_on_success
def edit(request, id):
    investigation = Investigation.objects.get(pk=id)
    if request.method == 'POST':
        description = investigation.description
        description.content = request.POST['description']
        description.save()
        #revision.user = request.user
    return HttpResponseRedirect(request.META["HTTP_REFERER"])

@login_required
def overview(request, id):
    investigation = Investigation.objects.get(pk=id)
    investigationform = InvestigationForm()
    #startdate = UserFile.objects.all().order_by("timecreated")[:1][0].timecreated.strftime('%Y %m %d %H:%M:%S')
    stream = activity_stream()
    people = get_people(investigation)
    files = []
    for ref in investigation.reference.all():
        ref_files = UserFile.objects.filter(reference=ref)
        for file in ref_files:
            if file not in files:
                files.append(files)
    return render_to_response('apps/investigation/overview.html', {'investigation': investigation, 'investigationform': investigationform, 'stream': stream, 'people': people, 'files':files}, RequestContext(request))

@login_required
def wiki(request, id):
    investigation = Investigation.objects.get(pk=id)
    people = get_people(investigation)
    return render_to_response('apps/investigation/wiki.html', {'investigation': investigation, 'people': people}, RequestContext(request))

@login_required
def timeline(request, id):
    investigation = Investigation.objects.get(pk=id)
    files = []
    for ref in investigation.reference.all():
        f = UserFile.objects.filter(reference=ref)
        for file in f:
            files.append(file)
    people = get_people(investigation)
    startdate = investigation.timecreated.strftime('%Y %m %d %H:%M:%S')
    return render_to_response('apps/investigation/timeline.html', {'investigation': investigation, 'startdate': startdate, 'files': files, 'people': people}, RequestContext(request))

@login_required
def library(request, id):
    investigation = Investigation.objects.get(pk=id)
    files = []
    for ref in investigation.reference.all():
        ref_files = UserFile.objects.filter(reference=ref)
        for file in ref_files:
            if file not in files:
                files.append(file)
    people = get_people(investigation)
    return render_to_response('apps/investigation/library.html', {'investigation': investigation, 'files': files, 'people': people}, RequestContext(request))

@login_required
def graph(request, id):
    investigation = Investigation.objects.get(pk=id)
    return render_to_response('apps/investigation/graph.html', {'investigation': investigation}, RequestContext(request))

@login_required
#@revision.create_on_success
def page(request, investigation_id, page_id=None):
    page = None
    investigation = Investigation.objects.get(pk=investigation_id)
    if page_id:
        page = Page.objects.get(pk=page_id)
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        page, created = Page.objects.get_or_create(title=title, creator=request.user, content=content)
        investigation.pages.add(page)
        url = "/investigation/%i/page/%i" % (investigation.id, page.id)
        return HttpResponseRedirect(url)
    return render_to_response('apps/investigation/page.html', {'investigation': investigation, 'page': page}, RequestContext(request))

@login_required
def add_reference(request, id):
    investigation = Investigation.objects.get(id=id)
    if request.method == "POST":
        reference, created = Reference.objects.get_or_create(name=request.POST['reference'])
        reference.users.add(request.user)
        investigation.reference.add(reference)
    return HttpResponseRedirect(request.META["HTTP_REFERER"])