from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from web.utils import *
from web.apps.investigation.models import Investigation
from web.apps.report.forms import UploadFileForm
from web.apps.report.models import UserFile
from web.utils import activity_stream

@login_required
def dashboard(request):
    files = UserFile.objects.filter(user=request.user).order_by('-time_created')
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
def inventory(request):
    investigations = Investigation.objects.filter(creator=request.user).order_by('-last_updated')
    files = UserFile.objects.filter(user=request.user)
    references = request.user.reference_set.all()
    return render_to_response('userprofile/inventory.html',
                                                                {
                                                                    'investigations': investigations,
                                                                    'files': files,
                                                                    'references': references,

                                                                }, RequestContext(request))

@login_required
def reading_list(request):
    investigations = Investigation.objects.filter(creator=request.user).order_by('-last_updated')
    return render_to_response('userprofile/reading_list.html',
                                                                    {
                                                                        'investigations': investigations,
                                                                    }, RequestContext(request))

@login_required
def suggestions(request):
    investigations = Investigation.objects.filter(creator=request.user).order_by('-last_updated')
    return render_to_response('userprofile/suggestions.html',
                                                                    {
                                                                        'investigations': investigations,
                                                                    }, RequestContext(request))

@login_required
def profile(request, user_id):
    user = User.objects.get(id=user_id)
    files = UserFile.objects.filter(user=user)
    return render_to_response('userprofile/dashboard.html',
                                                                  {
                                                                      'files': files,
                                                                      'requser': user
                                                                  }, RequestContext(request))

