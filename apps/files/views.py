# Django stuff
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.comments.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Imports from this application
from utils import handle_uploaded_file
from forms import *
from models import *

# Tagging
from tagging.models import *
from tagging.utils import *

# Imports from other fordrop-apps 
from fordrop.apps.malware.models import *
from fordrop.apps.search.forms import *
from fordrop.utils import *

# fordrop settings
from fordrop.settings import FD_FILEBASEPATH, FD_AUTHORIZATION_FILE

# System
import os
import re

@login_required
def index(request):
    uploadform = UploadFileForm()
    searchform = SearchForm()
    files = UserFile.objects.all().order_by('-timecreated')[:10]
    comments = Comment.objects.all().order_by('-submit_date')[:3]
    tagcloud = Tag.objects.cloud_for_model(File,  steps=5, distribution=LOGARITHMIC, filters=None, min_count=None)
    return render_to_response(
                              'apps/files/index.html', 
                              {
                                    'uploadform':   uploadform, 
                                    'searchform':   searchform, 
                                    'files':        files, 
                                    'comments':     comments, 
                                    'tagcloud':     tagcloud
                              }, RequestContext(request))

@login_required
def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            result = handle_uploaded_file(request.FILES['file'])
            # Check if upload of file was successful
            if result == None:
                return render_to_response('apps/files/error.html', {}, RequestContext(request))
            # Create database entry
            file, created = File.objects.get_or_create(filesize=int(result['filesize']), filetype=result['filetype'], md5=result['md5'], sha1=result['sha1'], sha256=result['sha256'], datefolder=result['datefolder'])
            resultdb, created = UserFile.objects.get_or_create(user=request.user, file=file, filename=result['filename'])
            if created:
                messages.error(request, 'Already reported by you')
            else:
                messages.success(request, 'Thank you for your submission')
            url = "/files/%i/show" % file.id
            return HttpResponseRedirect(url)
        else:
            return HttpResponseRedirect("/files")
    else:
        return HttpResponseRedirect("/files")

@login_required
def file_show(request, file_id):
    searchform = SearchForm()
    file = File.objects.get(id=file_id)
    resultall = UserFile.objects.filter(file=file)
    tagform = TagForm()
    tags = Tag.objects.get_for_object(file)
    strings = None
    pe_dump = None
    filebasepath = FD_FILEBASEPATH
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
        refs = []
        for f in resultall:
            if f.reference not in refs and f.reference is not None:
                refs.append(f.reference)
        if len(refs) > 1:
            multiple_refs = True
            related = get_related(refs)
        else:
            multiple_refs = False
            related = False
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
                              'apps/files/show.html', 
                              {
                                    "multiple_hits":    multiple_hits,
                                    "multiple_refs":    multiple_refs, 
                                    'searchform':       searchform, 
                                    'result':           file, 
                                    'resultall':        resultall, 
                                    'resultme':         resultme, 
                                    'tagform':          tagform, 
                                    'tags':             tags, 
                                    'mhr':              mhr, 
                                    'strings':          strings, 
                                    'is_pefile':        is_pefile, 
                                    'pedump':           pe_dump
                              }, RequestContext(request))

@login_required
def editref(request, file_id):
    if request.method == 'POST':
        form = ReferenceForm(request.POST)
        if form.is_valid():
            _reference = form.cleaned_data['reference']
            try:
                reference = Reference.objects.get(reference=_reference)
            except:
                reference = Reference.objects.create(reference=_reference)
            reftag = Tag.objects.get_or_create(name=_reference)
            userfile = UserFile.objects.get(user=request.user, file=file_id)
            userfile.reference = reference
            userfile.save()
            url = "/files/%i/show" % int(file_id)
            return HttpResponseRedirect(url)
        else:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
    else:
        referenceform = ReferenceForm()
        userfile = UserFile.objects.get(user=request.user, file=file_id)
        return render_to_response('apps/files/editref.html', {'referenceform': referenceform, 'result': userfile}, RequestContext(request))
