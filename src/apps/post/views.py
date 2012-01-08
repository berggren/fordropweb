from uuid import uuid4
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from models import Post
from apps.investigation.models import Investigation
from apps.report.models import File
from apps.boxes.models import Box

@login_required
def post(request):
    if request.method == 'POST':
        print request.POST
        type = request.POST['type']
        post = request.POST['post']
        boxes = request.POST.getlist('boxes')
        if not post:
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        if type == "user":
            object = request.user
        elif type == "investigation":
            object = Investigation.objects.get(pk=request.POST['id'])
        elif type == "file":
            object = File.objects.get(pk=request.POST['id'])
        p = Post.objects.create(post=post, content_object=object, author=request.user, uuid=uuid4().urn)
        if boxes:
            for box in boxes:
                b = Box.objects.get(node=box)
                p.boxes.add(b)
                p.published = False
                p.save()
        return HttpResponseRedirect(request.META["HTTP_REFERER"])
    