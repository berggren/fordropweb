from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from apps.report.models import File
from apps.userprofile.models import UserProfile
from apps.investigation.models import Investigation

@login_required
def search(request):
    if request.method == 'POST':
        data = request.POST ['search']
        if data == "":
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        files = File.objects.filter(Q(filesize__icontains=data)|
                                    Q(filetype__icontains=data)|
                                    Q(md5__icontains=data)|
                                    Q(sha1__icontains=data)|
                                    Q(filename__icontains=data)|
                                    Q(sha256__icontains=data))
        file_list = [x for x in files]
        for f in File.objects.filter(tags__name__in=[data]):
            if not f in files:
                file_list.append(f)
        users = User.objects.filter(Q(username__icontains=data))
        user_list = [x for x in users]
        user_profiles = UserProfile.objects.filter(Q(name__icontains=data)|Q(email__icontains=data)|Q(location__icontains=data)|Q(web__icontains=data)|Q(bio__icontains=data))
        for u in user_profiles:
            if not u.user in user_list:
                user_list.append(u.user)
        investigations = Investigation.objects.filter(title__icontains=data)
        investigation_list = [x for x in investigations]
        for i in Investigation.objects.filter(tags__name__in=[data]):
            if not i in investigation_list:
                investigation_list.append(i)
        return render_to_response('search/result.html',
                                                            {'data': data,
                                                             'files': file_list,
                                                             'users': user_list,
                                                             'investigations': investigation_list,
                                                             'site_name': request.get_host(),
                                                            }, RequestContext(request))
    else:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    
