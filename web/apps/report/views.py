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
from settings import FD_FILEBASEPATH, FD_AUTHORIZATION_FILE
from web.apps.investigation.models import Investigation
from web.graphutils import FordropGraphClient


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
            file, file_created = File.objects.get_or_create(filesize=int(result['filesize']),
                                                       filetype=result['filetype'],
                                                       md5=result['md5'],
                                                       sha1=result['sha1'],
                                                       sha256=result['sha256'],
                                                       datefolder=result['datefolder'])
            user_file, uf_created = UserFile.objects.get_or_create(user=request.user,
                                                                file=file,
                                                                filename=result['filename'])
            if uf_created:
                gc = FordropGraphClient()
                gc.add_node(request, file, "file")
                gc.add_relationship(request.user.get_profile().graph_id, file.graph_id, "reported")
            else:
                messages.error(request, 'Already reported by you')
            url = "/file/%i/show" % file.id
            return HttpResponseRedirect(url)
    else:
        file = File.objects.get(id=file_id)
        files = UserFile.objects.filter(file=file)
        investigations = None
        refs = []
        for f in files:
            if f.reference not in refs and f.reference is not None:
                refs.append(f.reference)
        try:
            mhr = MalwareMhr.objects.get(file=file)
        except:
            mhr = None
        try:
            resultme = UserFile.objects.get(user=request.user, file=file)
        except: resultme = None
        for ref in refs:
            investigations = Investigation.objects.filter(reference__name__exact=ref)
        return render_to_response(
                                  'apps/report/file.html',
                                  {
                                        "investigations":   investigations,
                                        'result':           file,
                                        'files':            files,
                                        'resultme':         resultme,
                                        'mhr':              mhr,
                                        'refs':             refs
                                  }, RequestContext(request))


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
    graph = FordropGraphClient()
    file = File.objects.get(id=id)
    print file
    related = json.loads(graph.get_related2(file.graph_id))['nodes']
    people = []
    investigations = []
    files = []
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
def wiki(request, id):
    file = File.objects.get(id=id)
    return render_to_response(
                              'apps/report/wiki.html',
                              {
                                    'file':           file,
                                    'result':           file,
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
