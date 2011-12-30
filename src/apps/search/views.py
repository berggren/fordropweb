from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from apps.report.models import File

@login_required
def search(request):
    if request.method == 'POST':
        data = request.POST ['search']
        if data == "":
            return HttpResponseRedirect("/")
        files = File.objects.filter(Q(filesize__icontains=data)|
                                    Q(filetype__icontains=data)|
                                    Q(md5__icontains=data)|
                                    Q(sha1__icontains=data)|
                                    Q(filename__icontains=data)|
                                    Q(sha256__icontains=data))
        return render_to_response('apps/search/result.html',
                                                            {'data': data,
                                                             'files': files
                                                            }, RequestContext(request))
    else:
        return HttpResponseRedirect("/")
    
