from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
from django.contrib import databrowse

# Databrowse
#from django.contrib import databrowse
#from fordrop.apps.upload.models import *
#databrowse.site.register(File)
#databrowse.site.register(UserFile)

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^fordrop/', include('fordrop.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),

    # fordrop
    (r'^$',                             'fordrop.views.index'),
    (r'^tag/add/(\w+)/(\d+)$',          'fordrop.views.add_tag'),
    (r'^reference/add/(\w+)/(\d+)$',    'fordrop.views.add_reference'),
    (r'^timeline$',                     'fordrop.views.timeline'),
    
    # Investigation
    (r'^investigation$',             'fordrop.apps.investigation.views.index'),
    (r'^investigation/(\d+)$',       'fordrop.apps.investigation.views.show'),
    (r'^investigation/create$',      'fordrop.apps.investigation.views.create'),
    
    # Upload & Files
    (r'^upload$',                     'fordrop.apps.upload.views.index'),
    (r'^file/(\d+)/show$',            'fordrop.apps.upload.views.show'),
    (r'^file/(\d+)/malware/mhr$',     'fordrop.apps.upload.views.get_malware_mhr'),

    # Reports
    (r'^report$',                     'fordrop.apps.report.views.index'),
    (r'^report/add$',                 'fordrop.apps.report.views.add'),
    (r'^report/(\d+)/show$',          'fordrop.apps.report.views.show'),

    # User
    (r'^user/(\d+)$',               'fordrop.apps.userprofile.views.index'),
    
    # Search
    (r'^search$',                   'fordrop.apps.search.views.search'),
    (r'^search/reference$',         'fordrop.apps.search.views.getref'),
    (r'^search/tag$',               'fordrop.apps.search.views.search_tag'),
    
    # Comments
    (r'^comments/',                 include('django.contrib.comments.urls')),
    
    # Login
    (r'^accounts/login/$', login,       {'template_name': "login.html"}),
    (r'^accounts/login-federated/$',    'fordrop.apps.fedlogin.views.fedlogin'),
    (r'^accounts/logout/$',             'fordrop.apps.fedlogin.views.fedlogout'),
    (r'^accounts/register/$',           'fordrop.apps.fedlogin.views.fedregister'),

    # Media
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/jbn/Documents/Aptana Studio 3 Workspace/fordrop/static', 'show_indexes': True}),
    (r'^databrowse/(.*)', databrowse.site.root),
)
