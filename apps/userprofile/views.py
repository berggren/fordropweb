from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext
from fordrop.apps.upload.models import *
from fordrop.apps.search.forms import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from fordrop.forms import *

@login_required
def index(request, user_id):
    searchform = SearchForm()
    user = User.objects.get(id=user_id)
    files = UserFile.objects.filter(user=user)
    return render_to_response('apps/userprofile/index.html', {'searchform': searchform, 'files': files, 'requser': user}, RequestContext(request))

@login_required
def edit(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = UserProfile.objects.get_or_create(user=user) 
            return HttpResponseRedirect('/user/home')
    else:
        form = ProfileForm()
    return render_to_response('apps/userprofile/edit.html', {'form': form}, RequestContext(request))
