from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
import uuid
import urllib2
from django.views.decorators.csrf import csrf_exempt
import json
from django_fordrop.forms import UserProfileForm
from django_fordrop.models import UserProfile, UserSettings, PubSubNode
from forms import UploadFileForm, FileCommentForm, CollectionCommentForm, CollectionForm, FileTagForm, UserProfileForm, UserSettingsForm, CollectionTagForm
from models import handle_uploaded_file, File, Collection, xmpp, notify_by_mail

@login_required
def index(request):
    collections = Collection.objects.all()[:5]
    my_collections = Collection.objects.filter(followers__username=request.user.username)
    tags_set = []
    for collection in my_collections:
        for tag in collection.tags.all():
            if not tag in tags_set:
                tags_set.append(tag)
    tracked_files = File.objects.filter(tags__in=tags_set)
    my_files = File.objects.filter(user=request.user)
    f = tracked_files | my_files
    files = f.order_by('-time_updated').distinct()[:10]
    return render_to_response("index.html", {'uploadform': UploadFileForm,
                                                 'commentform': FileCommentForm,
                                                 'collectionform': CollectionForm,
                                                 'collections': collections,
                                                 'nodes': PubSubNode.objects.all(),
                                                 'files': files}, RequestContext(request))

@login_required
def file(request, id):
    file = File.objects.get(pk=id)
    is_reporter = file.is_reporter(request.user)
    return render_to_response("file.html", {'file': file,
                                            'is_reporter': is_reporter,
                                            'tagform': FileTagForm(instance=file),
                                            'commentform': FileCommentForm}, RequestContext(request))

@login_required
def file_tag(request, id):
    file = File.objects.get(pk=id)
    if request.method == 'POST':
        form = FileTagForm(request.POST, instance=file)
        if form.is_valid():
            form.save()
        if file.tags.all:
            for node in file.nodes.all():
                xmpp.publish(node=node.node, payload=file.activity_tags())
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def collection(request):
    if request.method == 'POST':
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.user = request.user
            collection.uuid = uuid.uuid4().urn
            collection.save()
            collection.followers.add(request.user)
            collection.save()
            form.save_m2m()
            for n in request.POST.getlist('nodes'):
                node = PubSubNode.objects.get(node=int(n))
                collection.nodes.add(node)
                xmpp.publish(node=node.node, payload=collection.activity_fordrop_collection())
                if collection.tags.all():
                    xmpp.publish(node=node.node, payload=collection.activity_tags())
    return HttpResponseRedirect('/collection/%s' % collection.id)

@login_required
def explore(request):
    return render_to_response("explore.html", {'collections': Collection.objects.all().order_by('-time_updated'), 'users': User.objects.filter(is_active=True), 'files': File.objects.all()}, RequestContext(request))

@login_required
def collection_tag(request, id):
    collection = Collection.objects.get(pk=id)
    if request.method == 'POST':
        form = CollectionTagForm(request.POST, instance=collection)
        if form.is_valid():
            form.save()
        if collection.tags.all:
            for node in collection.nodes.all():
                xmpp.publish(node=node.node, payload=collection.activity_tags())
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def collection_timeline(request, id):
    collection = Collection.objects.get(pk=id)
    try:
        startdate = collection.latest_file().time_created.strftime('%a %b %d %Y %H:%M:%S')
    except:
        startdate = collection.time_created.strftime('%a %b %d %Y %H:%M:%S')
    return render_to_response("collection_timeline.html", {'uploadform': UploadFileForm,
                                                           'collection': collection,
                                                           'commentform': FileCommentForm,
                                                           'tagform': CollectionTagForm(instance=collection),
                                                           'timeline': timeline_json,
                                                           'startdate': startdate}, RequestContext(request))

@login_required
def timeline_json(request, id):
    collection = Collection.objects.get(pk=id)
    return HttpResponse(collection.timeline())

@login_required
def file_comment(request, id):
    if request.method == 'POST':
        form = FileCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            file = File.objects.get(pk=id)
            comment.user = request.user
            comment.file = file
            comment.uuid = uuid.uuid4().urn
            comment.save()
            file.save()
            for node in file.nodes.all():
                xmpp.publish(node=node.node, payload=comment.activity())
            notify_by_mail(users=[f.user for f in file.get_reporters()], subject='New comment on one of your files - ' + file.sha1, body=comment.content, obj=comment)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def collection_comment(request, id):
    if request.method == 'POST':
        form = CollectionCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            collection = Collection.objects.get(pk=id)
            comment.user = request.user
            comment.collection = collection
            comment.uuid = uuid.uuid4().urn
            comment.save()
            collection.save()
            for node in collection.nodes.all():
                xmpp.publish(node=node.node, payload=comment.activity())
            notify_by_mail(users=collection.followers.all(), subject='New comment in - ' + collection.title, body=comment.content, obj=comment)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def collection_follow(request, id):
    if request.method == 'POST':
        collection = Collection.objects.get(pk=id)
        collection.followers.add(request.user)
        collection.save()
        for node in collection.nodes.all():
            xmpp.publish(node=node.node, payload=collection.activity_follow())
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def collection_unfollow(request, id):
    if request.method == 'POST':
        collection = Collection.objects.get(pk=id)
        collection.followers.remove(request.user)
        collection.save()
        for node in collection.nodes.all():
            xmpp.publish(node=node.node, payload=collection.activity_unfollow())
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def file_share(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            result = handle_uploaded_file(request.FILES['file'])
            if result:
                try:
                    file = File.objects.get(sha512=result['sha512'], user=request.user)
                    messages.error(request, 'You have already reported this file')
                    return HttpResponseRedirect('/file/%s' % file.id)
                except ObjectDoesNotExist:
                    file = form.save(commit=False)
                    file.uuid = uuid.uuid4().urn
                    file.user = request.user
                    file.filename = result['filename']
                    file.filesize = result['filesize']
                    file.md5 = result['md5']
                    file.sha1 = result['sha1']
                    file.sha256 = result['sha256']
                    file.sha512 = result['sha512']
                    file.save()
                    form.save_m2m()
                    for n in request.POST.getlist('nodes'):
                        node = PubSubNode.objects.get(node=int(n))
                        file.nodes.add(node)
                        xmpp.publish(node=node.node, payload=file.activity_fordrop_file())
                        if file.tags.all():
                            xmpp.publish(node.node, payload=file.activity_tags())

                    print json.dumps(file.activity_fordrop_file(), indent=4)
                    messages.success(request, "Sharing is caring, file successfully recieved!")
                    notify_by_mail(users=[file.user for file in file.get_reporters()], subject='Hey, someone reported the same file as you', body=file.sha1, obj=file)
    return HttpResponseRedirect('/file/%s' % file.id)

@login_required
def file_clone(request, id):
    ref_file = File.objects.get(pk=id)
    if request.user in [file.user for file in ref_file.get_reporters()]:
        messages.error(request, 'You have already reported this file')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    file = File.objects.create(
        uuid = uuid.uuid4().urn,
        user = request.user,
        filename = ref_file.filename,
        filesize = ref_file.filesize,
        md5 = ref_file.md5,
        sha1 = ref_file.sha1,
        sha256 = ref_file.sha256,
        sha512 = ref_file.sha512
    )
    for tag in ref_file.tags.all():
        file.tags.add(tag)
    for node in ref_file.nodes.all():
        file.nodes.add(node)
        xmpp.publish(node=node.node, payload=file.activity_tags())
        if file.tags.all():
            xmpp.publish(node.node, payload=file.activity_tags())
    file.save()
    notify_by_mail(users=[file.user for file in file.get_reporters()], subject='Hey, someone reported the same file as you', body=file.sha1, obj=file)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def search(request):
    if request.method == 'POST':
        data = request.POST ['search']
    elif request.GET.get('q', ''):
        data = urllib2.unquote(request.GET.get('q', ''))
    else:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    if data.startswith('tag:'):
        data = data.replace('tag:', '').lstrip()
        files = File.objects.filter(tags__name=data)
    else:
        files = File.objects.filter(
            Q(filename__icontains=data)|
            Q(md5__icontains=data)|
            Q(sha1__icontains=data)|
            Q(sha256__icontains=data)|
            Q(sha512__icontains=data))
    return render_to_response("search.html", {'files': files}, RequestContext(request))

@login_required
def profile(request, id=None):
    if not id:
        profile_user = request.user
    else:
        profile_user = User.objects.get(pk=id)
    if profile_user == request.user:
        tmpl = 'profile.html'
    else:
        tmpl = 'profile.html'
    files = File.objects.filter(user=profile_user)
    collections = Collection.objects.filter(followers__username=profile_user.username)
    return render_to_response(tmpl, {'profile_user': profile_user,
                                     'files': files,
                                     'collections': collections}, RequestContext(request))

@login_required
@csrf_exempt
def add_pubsub_node(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            j = json.loads(request.POST.keys()[0])
            PubSubNode.objects.get_or_create(name=j.get('name'), node=j.get('node'))
        return HttpResponse(True)
    else:
        return PermissionDenied

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_settings, created = UserSettings.objects.get_or_create(user=request.user)
    form = UserProfileForm(instance=profile)
    settingsform = UserSettingsForm(instance=user_settings)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            if request.POST.get('welcome', False):
                redir_url = "/welcome/2"
            else:
                redir_url = request.META["HTTP_REFERER"]
                messages.success(request, 'Profile saved!')
            return HttpResponseRedirect(redir_url)
    return render_to_response('edit_profile.html',{'form': form,
                                                   'settingsform': settingsform}, RequestContext(request))

@login_required
def edit_settings(request):
    user_settings, created = UserSettings.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=user_settings)
        if form.is_valid():
            form.save()
            if request.POST.get('welcome', False):
                redir_url = "/welcome/3"
            else:
                redir_url = request.META["HTTP_REFERER"]
                messages.success(request, 'Settings saved!')
        return HttpResponseRedirect(redir_url)

@login_required
def federation(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    return render_to_response('pubsubbox.html',{}, RequestContext(request))

@login_required
def welcome(request, id=None):
    tmpl = 'welcome_step_0.html'
    if id == "1":
        tmpl = 'welcome_step_1.html'
    if id == "2":
        tmpl = 'welcome_step_2.html'
    if id == "3":
        tmpl = 'welcome_step_3.html'
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_settings, created = UserSettings.objects.get_or_create(user=request.user)
    form = UserProfileForm(instance=profile)
    settingsform = UserSettingsForm(instance=user_settings)
    return render_to_response(tmpl,{'form': form, 'settingsform': settingsform}, RequestContext(request))
