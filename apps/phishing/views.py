from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from forms import *
from models import *
from django.http import Http404
from tagging.models import *
from tagging.utils import *
from django.contrib.comments.models import *
from fordrop.apps.search.forms import *
from fordrop.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import re
import hashlib

@login_required
def index(request):
    phishingform = PhishingForm()
    searchform = SearchForm()
    phish = UserPhishing.objects.all()
    tagcloud = Tag.objects.cloud_for_model(Phishing,  steps=5, distribution=LOGARITHMIC, filters=None, min_count=None)
    return render_to_response('apps/phishing/index.html', {'phish': phish, 'phishingform': phishingform, 'searchform': searchform, 'tagcloud': tagcloud}, RequestContext(request))

@login_required
def add(request):
    if request.method == 'POST':
        form = PhishingForm(request.POST)
        if form.is_valid():
            formdata = form.cleaned_data['phish']
            md5 = hashlib.md5(formdata).hexdigest()
            sha1 = hashlib.sha1(formdata).hexdigest()
            sha256 = hashlib.sha256(formdata).hexdigest()
            if re.findall('[a-zA-Z0-9+_\-\.]+@[0-9a-zA-Z][.-0-9a-zA-Z]*.[a-zA-Z]+', formdata):
                phishing_type = "M" 
            else:
                phishing_type = "U"
            # Create database entry
            try:
                phishing = Phishing.objects.get(sha1=sha1)
            except:
                phishing = Phishing.objects.create(md5=md5, sha1=sha1, sha256=sha256)
            try:
                resultdb = UserPhishing.objects.get(user=request.user, phish=phishing)
                messages.error(request, 'Already reported by you')
            except:
                resultdb = UserPhishing.objects.create(user=request.user, phish=phishing, type=phishing_type, data=formdata)
                messages.success(request, 'Thank you for your submission')
            url = "/phishing/%i/show" % phishing.id
            return HttpResponseRedirect(url)
        else:
            return HttpResponseRedirect("/phishing")
    else:
        return HttpResponseRedirect("/phishing")
    
@login_required
def show(request, phish_id):
    searchform = SearchForm()
    tagform = TagForm()
    referensform = ReferenceForm()
    phishing = Phishing.objects.get(id=phish_id)
    resultall = UserPhishing.objects.filter(phish=phishing)
    tags = Tag.objects.get_for_object(phishing)
    try:
        resultme = UserPhishing.objects.get(user=request.user, phish=phishing)
    except: resultme = None
    return render_to_response('apps/phishing/show.html', {"referensform": referensform, "tagform": tagform, 'searchform': searchform, 'result': phishing, 'resultall': resultall, 'resultme': resultme, 'tags': tags}, RequestContext(request))

