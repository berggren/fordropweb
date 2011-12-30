from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout

from api import FileResource
from tastypie.api import Api

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(FileResource())

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),

    # fordrop
    (r'^$',                             'apps.userprofile.views.dashboard'),
    (r'^timeline/(\d+)$',               'views.timeline'),
    (r'^arbor$',                        'views.arbor'),

    # Home
    (r'^home$',                         'apps.userprofile.views.dashboard'),

    # Upload & Report
    (r'^file/(\d+)/show$',            'apps.report.views.file'),
    (r'^file/(\d+)/graph$',           'apps.report.views.graph'),
    (r'^file/(\d+)/related$',         'apps.report.views.related'),
    (r'^file/(\d+)/malware/mhr$',     'apps.report.views.get_malware_mhr'),
    (r'^report/add/file$',            'apps.report.views.file'),
    (r'^file/(\d+)/tag$',                   'apps.report.views.add_tag'),

    # Investigations
    (r'^investigation$',                            'apps.investigation.views.create'),
    (r'^investigation/(\d+)$',                      'apps.investigation.views.overview'),
    (r'^investigation/create$',                     'apps.investigation.views.create'),
    (r'^investigation/(\d+)/timeline$',             'apps.investigation.views.timeline'),
    (r'^investigation/(\d+)/graph$',                'apps.investigation.views.graph'),
    (r'^investigation/(\d+)/related$',              'apps.investigation.views.related'),
    (r'^investigation/(\d+)/tag$',                           'apps.investigation.views.add_tag'),

    # Pages
    (r'^pages/create$',             'apps.pages.views.create'),

    # Postss
    (r'^post$',             'apps.post.views.post'),

    # User
    (r'^user/(\d+)$',               'apps.userprofile.views.profile'),

    # Settings
    (r'^settings$',                         'apps.userprofile.views.edit_profile'),
    (r'^settings/profile$',                 'apps.userprofile.views.edit_profile'),
    (r'^settings/notifications$',           'apps.userprofile.views.edit_notifications'),
    (r'^settings/federation$',              'apps.userprofile.views.federation'),

    # Search
    (r'^search$',                   'apps.search.views.search'),

    # API
    (r'^api/',      include(v1_api.urls)),

    # Comments
    (r'^comments/',                 include('django.contrib.comments.urls')),
    
    # Login
    (r'^accounts/login/$', login,       {'template_name': "login.html"}),
    (r'^accounts/logout/$', logout,     {'template_name': "login.html"}),
    (r'^accounts/change_password/$',    'django.contrib.auth.views.password_change', {'post_change_redirect' : '/accounts/change_password/done/'}),
    (r'^accounts/change_password/done/$', 'django.contrib.auth.views.password_change_done'),

    # Media
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/jbn/stuff/work/code/fordrop/src/static', 'show_indexes': True}),
)
