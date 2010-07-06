# Django stuff
from django.http import HttpResponseRedirect, Http404, HttpResponse
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
from fordrop.apps.search.forms import *
from fordrop.utils import *
from fordrop.forms import *

# fordrop settings
from fordrop.settings import FD_FILEBASEPATH, FD_AUTHORIZATION_FILE

# System
import os
import re

@login_required
def index(request):
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
        files = UserFile.objects.all().order_by('-timecreated')[:10]
        comments = Comment.objects.all().order_by('-submit_date')[:3]
        tagcloud = Tag.objects.cloud_for_model(File,  steps=5, distribution=LOGARITHMIC, filters=None, min_count=None)
        return render_to_response(
                                  'apps/upload/index.html', 
                                  {
                                    'uploadform':   uploadform, 
                                    'searchform':   searchform, 
                                    'files':        files, 
                                    'comments':     comments, 
                                    'tagcloud':     tagcloud
                                  }, RequestContext(request))

@login_required
def show(request, file_id):
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
                              'apps/upload/show.html', 
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