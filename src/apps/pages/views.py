from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from models import *
from reversion import revision

@login_required
@revision.create_on_success
def create(request):
    """
    Create page
    """
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        page, created = Page.objects.get_or_create(title=title, creator=request.user, content=content)
        url = "/pages/%i" % page.id
        return HttpResponseRedirect(url)
    return render_to_response("apps/pages/create.html", {}, RequestContext(request))

