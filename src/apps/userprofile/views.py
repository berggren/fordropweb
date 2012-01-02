from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from apps.userprofile.models import UserProfile, UserSettings
from utils import *
from apps.investigation.models import Investigation
from apps.report.forms import UploadFileForm
from apps.report.models import File
from utils import activity_stream, user_activity_stream
from forms import UserProfileForm, UserNotificationForm, UserVisibilityForm


@login_required
def dashboard(request):
    files = File.objects.filter(user=request.user).order_by('-time_created')[:10]
    stream = activity_stream()
    upload_form = UploadFileForm()
    investigations = Investigation.objects.filter(creator=request.user).order_by('-last_updated')
    return render_to_response('userprofile/dashboard.html',
                                                                {
                                                                    'investigations': investigations,
                                                                    'stream': stream,
                                                                    'files': files,
                                                                    'uploadform': upload_form,
                                                                    'request': request
                                                                }, RequestContext(request))

@login_required
def federation(request):
    return render_to_response('userprofile/federation.html',
                                                                    {
                                                                    }, RequestContext(request))

@login_required
def profile(request, user_id):
    profile_user = User.objects.get(pk=user_id)
    stream = user_activity_stream(profile_user.id)
    investigations = Investigation.objects.filter(creator=profile_user).order_by('-last_updated')
    return render_to_response('userprofile/profile.html',{'profile_user': profile_user, 'form': UserProfileForm, 'stream': stream, 'investigations': investigations}, RequestContext(request))
@login_required

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    form = UserProfileForm(instance=profile)
    if request.method == 'POST':
            form = UserProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.error(request, 'Profile saved!')
                return HttpResponseRedirect(request.META["HTTP_REFERER"])
    return render_to_response('userprofile/edit_profile.html',{'form': form}, RequestContext(request))

@login_required
def edit_notifications(request):
    user_settings, created = UserSettings.objects.get_or_create(user=request.user)
    form = UserNotificationForm(instance=user_settings)
    if request.method == 'POST':
        form = UserNotificationForm(request.POST, instance=user_settings)
        form.save()
        messages.error(request, 'Notification settings saved!')
        return HttpResponseRedirect(request.META["HTTP_REFERER"])
    return render_to_response('userprofile/edit_notifications.html',{'form': form}, RequestContext(request))

@login_required
def edit_visibility(request):
    user_settings, created = UserSettings.objects.get_or_create(user=request.user)
    form = UserVisibilityForm(instance=user_settings)
    if request.method == 'POST':
        form = UserVisibilityForm(request.POST, instance=user_settings)
        form.save()
        messages.error(request, 'Notification settings saved!')
        return HttpResponseRedirect(request.META["HTTP_REFERER"])
    return render_to_response('userprofile/edit_visibility.html',{'form': form}, RequestContext(request))
