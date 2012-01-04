from uuid import uuid4
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from models import Post
from apps.investigation.models import Investigation
from apps.report.models import File

@login_required
def post(request):
    if request.method == 'POST':
        type = request.POST['type']
        post = request.POST['post']
        print request.POST
        if not post:
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        if type == "user":
            object = request.user
        elif type == "investigation":
            object = Investigation.objects.get(pk=request.POST['id'])
        elif type == "file":
            object = File.objects.get(pk=request.POST['id'])
        Post(post=post, content_object=object, author=request.user, uuid=uuid4().urn).save()
        return HttpResponseRedirect(request.META["HTTP_REFERER"])
    