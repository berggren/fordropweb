from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.comments.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from models import *
from tagging.models import *
from tagging.utils import *
from fordrop.utils import *

# Reversion
from reversion.models import Version
from reversion import revision
#from reversion.helpers import generate_patch

@login_required
@revision.create_on_success
def create(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        page, created = Page.objects.get_or_create(title=title, creator=request.user, content=content)
        url = "/pages/%i" % page.id
        return HttpResponseRedirect(url)
    return render_to_response("apps/pages/create.html", {}, RequestContext(request))

@login_required
@revision.create_on_success
def edit(request, storm_id, page_id):
    page = Page.objects.get(pk=page_id)
    if request.method == 'POST':
        content = request.POST['content']
        title = request.POST['title']
        page.title = title
        page.content = content
        page.save()
        revision.user = request.user
    return HttpResponseRedirect(request.META["HTTP_REFERER"])
