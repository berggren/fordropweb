from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext
from fordrop.apps.files.models import *
from fordrop.apps.search.forms import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

@login_required
def index(request, user_id):
    searchform = SearchForm()
    user = User.objects.get(id=user_id)
    files = UserFile.objects.filter(user=user)
    return render_to_response('apps/userprofile/index.html', {'searchform': searchform, 'files': files, 'requser': user}, RequestContext(request))
