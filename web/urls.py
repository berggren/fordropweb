from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout

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
    (r'^admin/', include(admin.site.urls)),

    # fordrop
    (r'^$',                             'apps.userprofile.views.dashboard'),
    (r'^tag/add/(\w+)/(\d+)$',          'views.add_tag'),
    (r'^reference/add/(\w+)/(\d+)$',    'views.add_reference'),
    (r'^timeline/(\d+)$',               'views.timeline'),

    # Home
    (r'^home$',                         'apps.userprofile.views.dashboard'),
    (r'^home/investigations$',               'apps.userprofile.views.my_investigations'),
    (r'^home/inventory$',               'apps.userprofile.views.inventory'),
    #(r'^home/inventory/json$',               'apps.userprofile.views.inventory_json'),
    (r'^home/readinglist$',               'apps.userprofile.views.reading_list'),
    (r'^home/suggestions$',               'apps.userprofile.views.suggestions'),

    # Upload & Report
    (r'^file/(\d+)/show$',            'apps.report.views.show_file'),
    (r'^file/(\d+)/malware/mhr$',     'apps.report.views.get_malware_mhr'),
    (r'^report$',                     'apps.report.views.report'),
    (r'^report/add$',                 'apps.report.views.add_report'),
    (r'^report/add/file$',            'apps.report.views.file'),
    (r'^report/(\d+)/show$',          'apps.report.views.show_file'),

    # Investigations
    (r'^investigation$',                            'apps.investigation.views.index'),
    (r'^investigation/(\d+)$',                      'apps.investigation.views.overview'),
    (r'^investigation/create$',                     'apps.investigation.views.create'),
    (r'^investigation/(\d+)/edit$',                 'apps.investigation.views.edit'),
    (r'^investigation/(\d+)/discussion$',           'apps.investigation.views.discussion'),
    (r'^investigation/(\d+)/timeline$',             'apps.investigation.views.timeline'),
    (r'^investigation/(\d+)/library$',              'apps.investigation.views.library'),
    (r'^investigation/(\d+)/page/(\d+)$',           'apps.investigation.views.page'),
    (r'^investigation/(\d+)/page/create$',          'apps.investigation.views.page'),

    # Pages
    (r'^pages/create$',             'apps.pages.views.create'),
    
    # User
    (r'^user/(\d+)$',               'apps.userprofile.views.profile'),
    (r'^user/edit$',                'apps.userprofile.views.edit_profile'),

    # Search
    (r'^search$',                   'apps.search.views.search'),
    (r'^search/reference$',         'apps.search.views.getref'),
    (r'^search/tag$',               'apps.search.views.search_tag'),
    
    # Comments
    (r'^comments/',                 include('django.contrib.comments.urls')),
    
    # Login
    (r'^accounts/login/$', login,       {'template_name': "login.html"}),
    (r'^accounts/login/federated/$',    'apps.auth.views.fedlogin'),
    (r'^accounts/login/local/$',        'apps.auth.views.local_login'),
    (r'^accounts/logout/$',             'apps.auth.views.fedlogout'),
    (r'^accounts/register/$',           'apps.auth.views.fedregister'),

    # Media
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/jbn/stuff/work/code/fordrop/web/static', 'show_indexes': True}),
)
