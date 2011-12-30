import json
from uuid import uuid4
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from utils import *
from forms import *
from models import *
from apps.investigation.models import *
from apps.search.forms import *
from settings import FD_FILEBASEPATH
from apps.investigation.models import Investigation
import graphutils as gc

@login_required
def file(request, file_id=None):
    """
    Handle upload file and show
    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            result = handle_uploaded_file(request.FILES['file'])
            if not result:
                return render_to_response('report/error.html', {}, RequestContext(request))
            file, created = File.objects.get_or_create(filesize=int(result['filesize']),
                                                       filename = result['filename'],
                                                       user = request.user,
                                                       filetype = result['filetype'],
                                                       md5=result['md5'],
                                                       sha1=result['sha1'],
                                                       sha256=result['sha256'],
                                                       uuid = uuid4().urn,
                                                       datefolder=result['datefolder'])
            if created:
                gc.add_node(gc.neo4jdb, request, file, "file")
                for f in File.objects.filter(sha256=file.sha256):
                    gc.add_relationship(gc.neo4jdb, request.user.profile.graph_id, f.graph_id, "reported")
            else:
                messages.error(request, 'Already reported by you')
            url = "/file/%i/show" % file.id
            return HttpResponseRedirect(url)
    else:
        file = File.objects.get(id=file_id)
        files = File.objects.filter(sha256=file.sha256)
        investigations = None
        try:
            mhr = MalwareMhr.objects.get(file=file)
        except:
            mhr = None
        return render_to_response(
                                  'apps/report/file.html',
                                  {
                                        "investigations":   investigations,
                                        'result':           file,
                                        'files':            files,
                                        'mhr':              mhr,
                                        'tagform':          TagForm()
                                  }, RequestContext(request))

@login_required
def add_tag(request, id):
    file = File.objects.get(pk=id)
    form = TagForm(request.POST, instance=file)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        for tag in form.cleaned_data['tags']:
            obj.tags.add(tag)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def graph(request, id):
    file = File.objects.get(id=id)
    return render_to_response(
                              'apps/report/graph.html',
                              {
                                    'file':           file,
                                    'result':           file,
                              }, RequestContext(request))

@login_required
def related(request, id):
    file = File.objects.get(id=id)
    try:
        related = json.loads(gc.get_related(gc.neo4jdb, file.graph_id))['nodes']
    except KeyError:
        related = None
    people = []
    investigations = []
    files = []
    if related:
        for k,v  in related.items():
            if v['web_id']:
                if v['type'] == 'person':
                    people.append(User.objects.get(pk=v['web_id']))
                if v['type'] == 'investigation':
                    investigations.append(Investigation.objects.get(pk=v['web_id']))
                if v['type'] == 'report':
                    files.append(File.objects.get(pk=v['web_id']))
    return render_to_response(
                              'apps/report/related.html',
                              {
                                    'file':             file,
                                    'result':           file,
                                    'people':           people,
                                    'investigations':   investigations,
                                    'files':            files,
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