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


@login_required
def index(request):
    searchform = SearchForm()
    startdate = UserFile.objects.all().order_by("timecreated")[:1][0].timecreated.strftime('%Y %m %d %H:%M:%S')
    return render_to_response('apps/investigation/index.html', {'searchform': searchform, 'startdate': startdate}, RequestContext(request))

def create(request):
    """
    ToDo: Input validation!!
    """
    if request.method == 'POST':
        references = []
        for key, value in request.POST.iteritems():
            if "reference_" in key and value == "on":
                references.append(key.split("_")[1])
        title = request.POST['title']
        investigation, created = Investigation.objects.get_or_create(title=title)
        for ref in references:
            reference = Reference.objects.get(name=ref)
            reference.investigation.add(investigation)
            reference.save()
        url = "/investigation/%i" % investigation.id
        return HttpResponseRedirect(url)

def show(request, id):
    investigation = Investigation.objects.get(pk=id)
    print investigation.reference_set.all()