from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from forms import *
from django.http import HttpResponseServerError
from django.core.mail import send_mail
from fordrop.settings import FD_MAILTO

def fedregister(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            remoteip = request.META['REMOTE_ADDR']
            remote_user = request.META['REMOTE_USER']
            name = form.cleaned_data['name']
            mail = form.cleaned_data['mail']
            subject = name+" is requesting access to fordrop"
            message = "Name: "+name+"\nEmail: "+mail+"\nIP-address: "+remoteip+"\nRemote user: "+remote_user  
            send_mail(subject, message, "fordrop@irt.kth.se", FD_MAILTO)
            return render_to_response('register.html', {}, RequestContext(request))
    else:
        form = RegisterForm()
    return render_to_response('register.html', {'form': form,}, RequestContext(request))

def fedlogin(request):
    remote_user = request.META['REMOTE_USER']
    remote_address = request.META['REMOTE_ADDR']
    if request.user.is_authenticated():
        update = False
        #if request.META.get("HTTP_GIVENNAME") == "(null)":
        #    return HttpResponseServerError()
        for attrib_name, meta_name in (("first_name", "HTTP_GIVENNAME"),
                                       ("last_name", "HTTP_SN"),
                                       ("email", "HTTP_MAIL")):
            attrib_value = getattr(request.user, attrib_name)
            meta_value = request.META.get(meta_name)
            if meta_value and not attrib_value:
                setattr(request.user, attrib_name, meta_value)
                update = True
        if request.user.password == "":
            request.user.password = "(not used for federated logins)"
            update = True
        if update:
            request.user.save()

        # Send mail
        subject = "fordrop: "+remote_user+" logged in from "+remote_address
        message = remote_user
        send_mail(subject, message, "fordrop@irt.kth.se", FD_MAILTO)
        #logger.info("Accepted federated login for user %s from %s" % (request.user.username, req_meta(request, "REMOTE_ADDR")))
        next = request.session.get("after_login_redirect", None)
        if next is not None:
            return HttpResponseRedirect(next)

    else:
        #logger.warning("Failed federated login for user %s from %s" % (request.user.username, req_meta(request, "REMOTE_ADDR")))
        # Send mail
        subject = "fordrop: "+remote_user+" FAILED to log in, not authorized. (from: "+remote_address+")"
        message = remote_user
        recipients = ['i@irt.kth.se']
        send_mail(subject, message, "fordrop@irt.kth.se", recipients)
        return HttpResponseRedirect("/accounts/register")
    return HttpResponseRedirect("/")

def fedlogout(request):
    logout(request)
    return HttpResponseRedirect("/Shibboleth.sso/Logout")