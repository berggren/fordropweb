import json
from uuid import uuid4
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.datastructures import MultiValueDictKeyError
from apps.pages.forms import PageForm
from apps.pages.models import Page
from apps.boxes.models import Box
from apps.post.models import NewPost
from utils import *
from forms import *
from models import File
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
        if not request.FILES:
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        if form.is_valid():
            result = handle_uploaded_file(request.FILES['file'])
            result_me = File.objects.filter(user=request.user, sha1=result['sha1'])
            if result_me:
                messages.error(request, 'Already reported by you')
                return HttpResponseRedirect(result_me[0].get_absolute_url())
            boxes = request.POST.getlist('boxes')
            file, created = File.objects.get_or_create(filesize=int(result['filesize']),
                                                       filename = result['filename'],
                                                       user = request.user,
                                                       filetype = result['filetype'],
                                                       md5=result['md5'],
                                                       sha1=result['sha1'],
                                                       sha256=result['sha256'],
                                                       sha512=result['sha512'],
                                                       ctph=result['ctph'],
                                                       uuid = uuid4().urn,
                                                       datefolder=result['datefolder'])

            if created:
                #gc.add_node(gc.neo4jdb, request, file, "file")
                #for f in File.objects.filter(sha256=file.sha256):
                #    gc.add_relationship(gc.neo4jdb, request.user.profile.graph_id, f.graph_id, "reported")
                try:
                    file.tags.add(request.POST['investigation'])
                except MultiValueDictKeyError:
                    pass
                if boxes:
                    for box in boxes:
                        b = Box.objects.get(node=box)
                        file.boxes.add(b)
                        file.published = False
                        file.save()
            return HttpResponseRedirect(file.get_absolute_url())
    else:
        file = File.objects.get(id=file_id)
        posts = NewPost.objects.filter(file=file).order_by('-time_created')[:10]
        files = File.objects.filter(sha256=file.sha256)
        tag_list = [x.name for x in file.tags.all()]
        investigations = Investigation.objects.filter(tags__name__in=tag_list).distinct()
        try:
            mhr = MalwareMhr.objects.get(file=file)
        except:
            mhr = None
        return render_to_response(
                                  'apps/report/file.html',
                                  {
                                        "investigations":   investigations,
                                        'result':           file,
                                        'file':             file,
                                        'files':            files,
                                        'posts':            posts,
                                        'mhr':              mhr,
                                        'tagform':          TagForm(),
                                        'descriptionform':  DescriptionForm(instance=file)
                                  }, RequestContext(request))
@login_required
def add_description(request, id):
    file = File.objects.get(pk=id)
    if request.user != file.user:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    form = DescriptionForm(request.POST)
    if form.is_valid():
        file.description = form.cleaned_data['description']
        file.save()
    else:
        print form.errors
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

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
    posts = file.posts.all().order_by('-time_created')[:10]
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
                                    'posts':            posts,
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

