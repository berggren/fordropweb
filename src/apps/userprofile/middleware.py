# -*- coding: utf-8 -*-
from django.contrib import messages
from django.http import HttpResponseRedirect

class FirstLoginMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated() and "dont_check_first_login" not in request.session:
            request.session["dont_check_first_login"] = True
            profile = request.user.profile
            if profile.is_first_login:
                profile.is_first_login = False
                profile.save()
                messages.error(request, 'Hello %s and welcome to fordrop!' % request.user.username)
                return HttpResponseRedirect("/")
