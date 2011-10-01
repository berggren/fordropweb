from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from web.apps.report.models import File, UserFile
from forms import SearchForm

@login_required
def search(request):
    form = SearchForm()
    if request.method == 'POST':
        data = form.cleaned_data['search']
        files = File.objects.filter(Q(filesize__icontains=data)|
                                    Q(filetype__icontains=data)|
                                    Q(md5__icontains=data)|
                                    Q(sha1__icontains=data)|
                                    Q(sha256__icontains=data))
        user_files = UserFile.objects.filter(Q(filename__icontains=data))
        return render_to_response('apps/search/result.html',
                                                            {'data': data,
                                                             'files': files,
                                                             'user_files': user_files
                                                            }, RequestContext(request))
    else:
        return HttpResponseRedirect("/")
    
