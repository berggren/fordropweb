from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import *
from django.http import Http404
from tagging.models import *
from tagging.utils import *
from django.contrib.comments.models import *
from apps.search.forms import *
from apps.report.models import *
from apps.pages.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from forms import *
from utils import *
from forms import *
from forms import *
import datetime

# Reversion
from reversion.models import Version
from reversion import revision
#from reversion.helpers import generate_patch

def get_people(investigation):
    people = []
    for ref in investigation.reference.all():
        ref_files = UserFile.objects.filter(reference=ref)
        for file in ref_files:
            if file.user == investigation.creator:
                continue
            if file.user not in people:
                people.append(file.user)
    return people

@login_required
def index(request): 
    searchform = SearchForm()
    investigations = Investigation.objects.all()
    newinvestigationform = NewInvestigationForm()
    return render_to_response('apps/investigation/index.html', {'searchform': searchform, 'investigations': investigations, 'newinvestigationform': newinvestigationform}, RequestContext(request))

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
        return HttpResponseRedirect(url)

@login_required
@revision.create_on_success
def edit(request, id):
    investigation = Investigation.objects.get(pk=id)
    if request.method == 'POST':
        description = investigation.description
        description.content = request.POST['description']
        description.save()
        revision.user = request.user
    return HttpResponseRedirect(request.META["HTTP_REFERER"])

@login_required
def overview(request, id):
    searchform = SearchForm()
    tagform = TagForm()
    investigation = Investigation.objects.get(pk=id)
    investigationform = InvestigationForm()
    startdate = UserFile.objects.all().order_by("timecreated")[:1][0].timecreated.strftime('%Y %m %d %H:%M:%S')
    stream = activity_stream()
    tags = Tag.objects.get_for_object(investigation)
    people = get_people(investigation)
    files = []
    for ref in investigation.reference.all():
        ref_files = UserFile.objects.filter(reference=ref)
        for file in ref_files:
            if file not in files:
                files.append(files)
    return render_to_response('apps/investigation/overview.html', {'searchform': searchform, 'investigation': investigation, 'investigationform': investigationform, 'startdate': startdate, 'stream': stream, 'tagform': tagform, 'tags': tags, 'people': people, 'files':files}, RequestContext(request))

@login_required
def discussion(request, id):
    searchform = SearchForm()
    investigation = Investigation.objects.get(pk=id)
    tagform = TagForm()
    tags = Tag.objects.get_for_object(investigation)
    people = get_people(investigation)
    return render_to_response('apps/investigation/discussion.html', {'searchform': searchform, 'investigation': investigation, 'tagform': tagform, 'tags': tags, 'people': people}, RequestContext(request))

@login_required
def timeline(request, id):
    searchform = SearchForm()
    investigation = Investigation.objects.get(pk=id)
    tagform = TagForm()
    tags = Tag.objects.get_for_object(investigation)
    files = []
    for ref in investigation.reference.all():
        files = UserFile.objects.filter(reference=ref)
        for file in files:
            if file not in files:
                files.append(files)
    people = get_people(investigation)
    startdate = investigation.timecreated.strftime('%Y %m %d %H:%M:%S')
    return render_to_response('apps/investigation/timeline.html', {'searchform': searchform, 'investigation': investigation, 'tagform': tagform, 'tags': tags, 'startdate': startdate, 'files': files, 'people': people}, RequestContext(request))

@login_required
def library(request, id):
    searchform = SearchForm()
    investigation = Investigation.objects.get(pk=id)
    tagform = TagForm()
    tags = Tag.objects.get_for_object(investigation)
    files = []
    for ref in investigation.reference.all():
        ref_files = UserFile.objects.filter(reference=ref)
        for file in ref_files:
            if file not in files:
                files.append(file)
    people = get_people(investigation)
    return render_to_response('apps/investigation/library.html', {'searchform': searchform, 'investigation': investigation, 'tagform': tagform, 'tags': tags, 'files': files, 'people': people}, RequestContext(request))

@login_required
@revision.create_on_success
def page(request, investigation_id, page_id=None):
    page = None
    tags = None
    searchform = SearchForm()
    tagform = TagForm()
    investigation = Investigation.objects.get(pk=investigation_id)
    if page_id:
        page = Page.objects.get(pk=page_id)
        tags = Tag.objects.get_for_object(page)
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        page, created = Page.objects.get_or_create(title=title, creator=request.user, content=content)
        investigation.pages.add(page)
        url = "/investigation/%i/page/%i" % (investigation.id, page.id)
        return HttpResponseRedirect(url)
    return render_to_response('apps/investigation/page.html', {'searchform': searchform, 'investigation': investigation, 'page': page, 'tagform': tagform, 'tags': tags}, RequestContext(request))

def browse(request):
    searchform = SearchForm()
    investigations = Investigation.objects.all()
    return render_to_response('apps/investigation/browse.html', {
                                                                'searchform': searchform,
                                                                'investigations': investigations,
                                                                }, RequestContext(request))
