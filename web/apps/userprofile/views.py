from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from apps.report.models import *
from apps.search.forms import *
from django.contrib.auth.decorators import login_required
from forms import *
from models import *
from utils import *
from web.apps.investigation.models import Investigation
from web.apps.search.forms import SearchForm

@login_required
def dashboard(request):
    files = UserFile.objects.filter(user=request.user).order_by('-timecreated')
    stream = activity_stream()
    investigations = Investigation.objects.filter(creator=request.user).order_by('-lastupdated')
    return render_to_response('apps/userprofile/dashboard.html',
                            {
                                'investigations': investigations,
                                'stream': stream,
                                'files': files
                            }, RequestContext(request))

@login_required
def inventory(request):
    investigations = Investigation.objects.filter(creator=request.user).order_by('-lastupdated')
    return render_to_response('apps/userprofile/inventory.html',
                            {
                                'investigations': investigations,
                            }, RequestContext(request))

@login_required
def reading_list(request):
    investigations = Investigation.objects.filter(creator=request.user).order_by('-lastupdated')
    return render_to_response('apps/userprofile/reading_list.html',
                            {
                                'investigations': investigations,
                            }, RequestContext(request))

@login_required
def suggestions(request):
    investigations = Investigation.objects.filter(creator=request.user).order_by('-lastupdated')
    return render_to_response('apps/userprofile/suggestions.html',
                            {
                                'investigations': investigations,
                            }, RequestContext(request))

@login_required
def profile(request, user_id):
    user = User.objects.get(id=user_id)
    files = UserFile.objects.filter(user=user)
    return render_to_response('apps/userprofile/dashboard.html',
                              {
                                  'searchform': searchform,
                                  'files': files,
                                  'requser': user
                              }, RequestContext(request))

@login_required
def edit_profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            email = form.cleaned_data['email']
            user.first_name = firstname
            user.last_name = lastname
            user.email = email
            user.save()
            return HttpResponseRedirect('/')
    else:
        form = ProfileForm({
            'firstname': request.user.first_name,
            'lastname': request.user.last_name,
            'email': request.user.email,
            'avatar':None
        })
    return render_to_response('apps/userprofile/edit.html',
                              {
                                  'form': form
                              }, RequestContext(request))
