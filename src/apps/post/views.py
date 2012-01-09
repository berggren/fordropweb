from uuid import uuid4
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from apps.investigation.models import Investigation
from apps.report.models import File
from apps.boxes.models import Box
from apps.post.models import Post, NewPost

@login_required
def post(request):
    if request.method == 'POST':
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

def new_post(request):
    if request.method == 'POST':
        content = request.POST['post']
        boxes = request.POST.getlist('boxes')
        type = request.POST['type']
        if not content:
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        post = NewPost.objects.create(content=content, user=request.user, uuid=uuid4().urn)
        if type == "file":
            file = File.objects.get(pk=request.POST['id'])
            post.file = file
            post.save()
            boxes = file.boxes.all()
        if type == "investigation":
            investigation = Investigation.objects.get(pk=request.POST['id'])
            post.investigation = investigation
            post.save()
            boxes = investigation.boxes.all()
        if boxes:
            for box in boxes:
                try:
                    b = Box.objects.get(node=box.node)
                except AttributeError:
                    b = Box.objects.get(node=box)
                post.boxes.add(b)
                post.published = False
                post.save()
        return HttpResponseRedirect(request.META["HTTP_REFERER"])
