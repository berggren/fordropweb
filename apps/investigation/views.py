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
from fordrop.apps.files.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def index(request):
    searchform = SearchForm()
    startdate = UserFile.objects.all().order_by("timecreated")[:1][0].timecreated.strftime('%Y %m %d %H:%M:%S')
    return render_to_response('apps/investigation/index.html', {'searchform': searchform, 'startdate': startdate}, RequestContext(request))

