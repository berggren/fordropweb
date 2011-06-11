from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from apps.investigation.models import *
from apps.report.models import *
from apps.report.forms import *
from forms import *
from django.db.models import Q
from tagging.models import *
from django.contrib.auth.decorators import login_required

@login_required
def search(request):
    searchform = SearchForm()
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['search']    
            files = File.objects.filter(Q(filesize__icontains=data)|Q(filetype__icontains=data)|Q(md5__icontains=data)|Q(sha1__icontains=data)|Q(sha256__icontains=data))
            userfiles = UserFile.objects.filter(Q(filename__icontains=data))
            return render_to_response('apps/search/result.html', {'searchform': searchform, 'data': data, 'files': files, 'userfiles': userfiles}, RequestContext(request))
        else:
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")

@login_required
def getref(request):
    searchform = SearchForm()
    if request.method == 'GET':
        _reference = request.GET['r']
        reference = Reference.objects.get(id=_reference)
        userfiles = UserFile.objects.filter(reference=reference)
        return render_to_response('apps/search/getref.html', {'searchform': searchform, 'reference': reference,'userfiles': userfiles}, RequestContext(request))

@login_required
def search_tag(request):
    searchform = SearchForm()
    if request.method == 'GET':
        tag = Tag.objects.get(id=request.GET['t'])
        _files = TaggedItem.objects.get_by_model(File, tag)
        files = []
        for file in _files:
            userfile = UserFile.objects.filter(file=file).order_by('timecreated')[:1]
            files.append(userfile)
        return render_to_response('apps/search/tags.html', {'searchform': searchform, 'files': files, 'tag': tag}, RequestContext(request))
