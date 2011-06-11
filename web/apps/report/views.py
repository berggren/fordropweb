# Django stuff
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.comments.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Imports from this application
from utils import *
from forms import *
from models import *

# Tagging
from tagging.models import *
from tagging.utils import *

# Imports from other fordrop-apps 
from apps.investigation.models import *
from apps.search.forms import *

# fordrop settings
from settings import FD_FILEBASEPATH, FD_AUTHORIZATION_FILE

# System
import os
import re
import hashlib

@login_required
def report(request):
    genericreportform = GenericReportForm()
    searchform = SearchForm()
    uploadform = UploadFileForm()
    reports = UserReport.objects.all()
    files = UserFile.objects.all()
    return render_to_response('apps/report/index.html', {
                                                            'reports': reports, 
                                                            'files': files,
                                                            'genericreportform': genericreportform,
                                                            'searchform': searchform,
                                                            'uploadform': uploadform,
                                                        }, RequestContext(request))

@login_required
def add_report(request):
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
            return HttpResponseRedirect("/upload")
    else:
        return HttpResponseRedirect("/upload")

@login_required
def file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            result = handle_uploaded_file(request.FILES['file'])
            # Check if upload of file was successful
            if result == None:
                return render_to_response('apps/upload/error.html', {}, RequestContext(request))
            # Create database entry
            file, created = File.objects.get_or_create(filesize=int(result['filesize']), filetype=result['filetype'], md5=result['md5'], sha1=result['sha1'], sha256=result['sha256'], datefolder=result['datefolder'])
            resultdb, created = UserFile.objects.get_or_create(user=request.user, file=file, filename=result['filename'])
            if not created:
                messages.error(request, 'Already reported by you')
            else:
                messages.success(request, 'Thank you for your submission')
            url = "/file/%i/show" % file.id
            return HttpResponseRedirect(url)
        else:
            return HttpResponseRedirect("/upload")
    else:
        uploadform = UploadFileForm()
        searchform = SearchForm()
        genericreportform = GenericReportForm()
        files = UserFile.objects.all().order_by('-timecreated')
        tagcloud = Tag.objects.cloud_for_model(File,  steps=5, distribution=LOGARITHMIC, filters=None, min_count=None)
        return render_to_response(
                                  'apps/upload/dashboard.html',
                                  {
                                    'uploadform':   uploadform, 
                                    'searchform':   searchform,
                                    'genericreportform': genericreportform,
                                    'files':        files, 
                                    'tagcloud':     tagcloud
                                  }, RequestContext(request))

@login_required
def show_file(request, file_id):
    searchform = SearchForm()
    file = File.objects.get(id=file_id)
    resultall = UserFile.objects.filter(file=file)
    tagform = TagForm()
    referenceform = ReferenceForm()
    tags = Tag.objects.get_for_object(file)
    strings = None
    pe_dump = None
    filebasepath = FD_FILEBASEPATH
    refs = []
    if os.path.exists(filebasepath+"/"+file.datefolder+"/"+file.sha1+".pedump"):
        is_pefile = True
    else:
        is_pefile = False
    try:
        if request.GET['strings'] == "True":
            fh = open(filebasepath+"/"+file.datefolder+"/"+file.sha1+".strings", "r")
            strings = ""
            for line in fh.readlines():
                strings = strings+line
            fh.close()
    except: pass
    try:
        if request.GET['pedump'] == "True":
            fh = open(filebasepath+"/"+file.datefolder+"/"+file.sha1+".pedump", "r")
            pe_dump = ""
            for line in fh.readlines():
                pe_dump = pe_dump+line
            fh.close()
    except: pass

    if len(resultall) > 1:
        multiple_hits = True
        for f in resultall:
            if f.reference not in refs and f.reference is not None:
                refs.append(f.reference)
        if len(refs) > 1:
            multiple_refs = True
        else:
            multiple_refs = False
    else:
        multiple_hits = False
        multiple_refs = False
    try:
        mhr = MalwareMhr.objects.get(file=file)
    except:
        mhr = None
    try:
        resultme = UserFile.objects.get(user=request.user, file=file)
    except: resultme = None
    return render_to_response(
                              'apps/report/file.html',
                              {
                                    "multiple_hits":    multiple_hits,
                                    "multiple_refs":    multiple_refs, 
                                    'searchform':       searchform, 
                                    'result':           file, 
                                    'resultall':        resultall, 
                                    'resultme':         resultme, 
                                    'tagform':          tagform, 
                                    'referenceform':    referenceform, 
                                    'tags':             tags, 
                                    'mhr':              mhr, 
                                    'strings':          strings, 
                                    'is_pefile':        is_pefile, 
                                    'pedump':           pe_dump,
                                    'refs':             refs
                              }, RequestContext(request))

@login_required
def show_report(request, report_id):
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
    

@login_required
def get_malware_mhr(request, file_id):
    hash = request.GET['hash']
    file = File.objects.get(id=file_id)
    try:
        MalwareMhr.objects.get(file=file)
        return HttpResponseRedirect(request.META["HTTP_REFERER"])
    except:
        dt, percent = query_mhr(hash)
        if percent is None or dt is None:
            mhr = MalwareMhr.objects.create(file=file, donotexist=True)
        else:
            mhr = MalwareMhr.objects.create(file=file, percent=percent, timecreated_mhr=dt)
        return HttpResponseRedirect(request.META["HTTP_REFERER"])
