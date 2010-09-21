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
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from forms import *
from utils import *

@login_required
def index(request):
    searchform = SearchForm()
    investigations = Investigation.objects.all()
    newinvestigationform = NewInvestigationForm()
    return render_to_response('apps/investigation/index.html', {'searchform': searchform, 'investigations': investigations, 'newinvestigationform': newinvestigationform}, RequestContext(request))

def create(request):
    if request.method == 'POST':
        references = []
        for key, value in request.POST.iteritems():
            if "reference_" in key and value == "on":
                references.append(key.split("_")[1])
        title = request.POST['title']
        investigation, created = Investigation.objects.get_or_create(title=title, creator=request.user)
        for ref in references:
            reference = Reference.objects.get(name=ref)
            reference.investigation.add(investigation)
            reference.save()
        url = "/investigation/%i" % investigation.id
        return HttpResponseRedirect(url)

def edit(request, id):
    investigation = Investigation.objects.get(pk=id)
    if request.method == 'POST':
        description = request.POST['description']
        investigation.description = description
        investigation.save()
    return HttpResponseRedirect(request.META["HTTP_REFERER"])

def show(request, id):
    searchform = SearchForm()
    investigation = Investigation.objects.get(pk=id)
    investigationform = InvestigationForm()
    startdate = UserFile.objects.all().order_by("timecreated")[:1][0].timecreated.strftime('%Y %m %d %H:%M:%S')
    stream = activity_stream()
    return render_to_response('apps/investigation/show.html', {'searchform': searchform, 'investigation': investigation, 'investigationform': investigationform, 'startdate': startdate, 'stream': stream}, RequestContext(request))

