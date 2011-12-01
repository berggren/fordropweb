from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),

    # fordrop
    (r'^$',                             'apps.userprofile.views.dashboard'),
    (r'^tag/add/(\w+)/(\d+)$',          'views.add_tag'),
    (r'^reference/add/(\w+)/(\d+)$',    'views.add_reference'),
    (r'^timeline/(\d+)$',               'views.timeline'),
    (r'^arbor$',                        'views.arbor'),
    (r'^related$',                      'views.related'),

    # Home
    (r'^home$',                         'apps.userprofile.views.dashboard'),
    (r'^home/inventory$',               'apps.userprofile.views.inventory'),
    (r'^home/readinglist$',               'apps.userprofile.views.reading_list'),
    (r'^home/suggestions$',               'apps.userprofile.views.suggestions'),

    # Upload & Report
    (r'^file/(\d+)/show$',            'apps.report.views.file'),
    (r'^file/(\d+)/graph$',           'apps.report.views.graph'),
    (r'^file/(\d+)/related$',         'apps.report.views.related'),
    (r'^file/(\d+)/wiki$',            'apps.report.views.wiki'),
    (r'^file/(\d+)/malware/mhr$',     'apps.report.views.get_malware_mhr'),
    (r'^report/add/file$',            'apps.report.views.file'),

    # Investigations
    (r'^investigation$',                            'apps.investigation.views.create'),
    (r'^investigation/(\d+)$',                      'apps.investigation.views.overview'),
    (r'^investigation/create$',                     'apps.investigation.views.create'),
    (r'^investigation/(\d+)/timeline$',             'apps.investigation.views.timeline'),
    (r'^investigation/(\d+)/graph$',                'apps.investigation.views.graph'),
    (r'^investigation/(\d+)/related$',                'apps.investigation.views.related'),
    (r'^investigation/(\d+)/wiki$',                 'apps.investigation.views.wiki'),
    (r'^investigation/(\d+)/reference/add$',        'apps.investigation.views.add_reference'),

    # Pages
    (r'^pages/create$',             'apps.pages.views.create'),

    # Postss
    (r'^post$',             'apps.post.views.post'),

    # User
    (r'^user/(\d+)$',               'apps.userprofile.views.profile'),

    (r'^federation$',                 'apps.userprofile.views.settings'),

    # Search
    (r'^search$',                   'apps.search.views.search'),

    # Comments
    (r'^comments/',                 include('django.contrib.comments.urls')),
    
    # Login
    (r'^accounts/login/$', login,       {'template_name': "login.html"}),
    (r'^accounts/logout/$', logout,     {'template_name': "login.html"}),

    # Media
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/jbn/stuff/work/code/fordrop/web/static', 'show_indexes': True}),
)
