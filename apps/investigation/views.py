from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import *
from django.http import Http404
from tagging.models import *
from tagging.utils import *
from django.contrib.comments.models import *
from fordrop.apps.search.forms import *
from fordrop.apps.upload.models import *
from fordrop.apps.pages.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from forms import *
from utils import *
import datetime
from fordrop.forms import *

# Reversion
from reversion.models import Version
from reversion import revision
from reversion.helpers import generate_patch

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
        description, created = Page.objects.get_or_create(title="Description", creator=request.user, content=None)
        investigation, created = Investigation.objects.get_or_create(title=title, creator=request.user, description=description)
        investigation.pages.add(description)
        for ref in references:
            reference = Reference.objects.get(name=ref)
            reference.investigation.add(investigation)
            reference.save()
        url = "/investigation/%i" % investigation.id
        return HttpResponseRedirect(url)

@login_required
@revision.create_on_success
def edit(request, id):
    investigation = Investigation.objects.get(pk=id)
    if request.method == 'POST':
        description_text = request.POST['description']
        description_title = request.POST['title']
        description = investigation.description
        description.title = description_title
        description.content = description_text
        description.save()
        revision.user = request.user
    return HttpResponseRedirect(request.META["HTTP_REFERER"])

@login_required
def overview(request, id):
    searchform = SearchForm()
    tagform = TagForm()
    investigation = Investigation.objects.get(pk=id)
    description = investigation.description
    investigationform = InvestigationForm()
    startdate = UserFile.objects.all().order_by("timecreated")[:1][0].timecreated.strftime('%Y %m %d %H:%M:%S')
    stream = activity_stream()
    tags = Tag.objects.get_for_object(investigation)
    return render_to_response('apps/investigation/overview.html', {'searchform': searchform, 'investigation': investigation, 'investigationform': investigationform, 'startdate': startdate, 'stream': stream, 'tagform': tagform, 'tags': tags}, RequestContext(request))

@login_required
def discussion(request, id):
    searchform = SearchForm()
    investigation = Investigation.objects.get(pk=id)
    tagform = TagForm()
    tags = Tag.objects.get_for_object(investigation)
    return render_to_response('apps/investigation/discussion.html', {'searchform': searchform, 'investigation': investigation, 'tagform': tagform, 'tags': tags}, RequestContext(request))

@login_required
def timeline(request, id):
    searchform = SearchForm()
    investigation = Investigation.objects.get(pk=id)
    tagform = TagForm()
    tags = Tag.objects.get_for_object(investigation)
    startdate = UserFile.objects.all().order_by("timecreated")[:1][0].timecreated.strftime('%Y %m %d %H:%M:%S')
    return render_to_response('apps/investigation/timeline.html', {'searchform': searchform, 'investigation': investigation, 'tagform': tagform, 'tags': tags, 'startdate': startdate}, RequestContext(request))

@login_required
def library(request, id):
    searchform = SearchForm()
    investigation = Investigation.objects.get(pk=id)
    tagform = TagForm()
    tags = Tag.objects.get_for_object(investigation)
    return render_to_response('apps/investigation/library.html', {'searchform': searchform, 'investigation': investigation, 'tagform': tagform, 'tags': tags}, RequestContext(request))

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
