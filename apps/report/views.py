from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from forms import *
from models import *
from tagging.models import *
from tagging.utils import *
from django.contrib.comments.models import *
from fordrop.apps.search.forms import *
from fordrop.apps.investigation.models import *
from fordrop.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import re
import hashlib

@login_required
def index(request):
    genericreportform = GenericReportForm()
    searchform = SearchForm()
    reports = UserReport.objects.all()
    tagcloud = Tag.objects.cloud_for_model(Report,  steps=5, distribution=LOGARITHMIC, filters=None, min_count=None)
    return render_to_response('apps/report/index.html', {
                                                            'reports': reports, 
                                                            'genericreportform': genericreportform, 
                                                            'searchform': searchform, 
                                                            'tagcloud': tagcloud
                                                        }, RequestContext(request))

@login_required
def add(request):
    if request.method == 'POST':
        form = GenericReportForm(request.POST)
        if form.is_valid():
            type = form.cleaned_data['type']
            value = form.cleaned_data['value']
            hash_string = unicode(type)+unicode(value)
            md5 = hashlib.md5(hash_string).hexdigest()
            sha1 = hashlib.sha1(hash_string).hexdigest()
            sha256 = hashlib.sha256(hash_string).hexdigest()
            # Create database entry
            report, created = Report.objects.get_or_create(type=type, value=value, md5=md5, sha1=sha1, sha256=sha256)
            user_report, created = UserReport.objects.get_or_create(user=request.user, report=report)
            if not created:
                messages.error(request, 'Already reported by you')
            else:
                messages.success(request, 'Thank you for your submission')
            url = "/report/%i/show" % report.id
            return HttpResponseRedirect(url)
        else:
            return HttpResponseRedirect("/report")
    else:
        return HttpResponseRedirect("/report")
    
@login_required
def show(request, report_id):
    searchform = SearchForm()
    referenceform = ReferenceForm()
    tagform = TagForm()
    report = Report.objects.get(id=report_id)
    resultall = UserReport.objects.filter(report=report)
    tags = Tag.objects.get_for_object(report)
    try:
        resultme = UserReport.objects.get(user=request.user, report=report)
    except: resultme = None
    return render_to_response('apps/report/show.html', {
                                                            "tagform": tagform, 
                                                            'searchform': searchform, 
                                                            'referenceform': referenceform, 
                                                            'result': report, 
                                                            'resultall': resultall, 
                                                            'resultme': resultme, 
                                                            'tags': tags
                                                          }, RequestContext(request))
    