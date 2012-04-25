from django.conf.urls import patterns, include, url
from django.contrib import admin
from tastypie.api import Api
from django_fordrop.api_v1 import FileResource, FileCommentResource, UserResource, UserProfileResource

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(FileResource())
v1_api.register(FileCommentResource())
v1_api.register(UserResource())
v1_api.register(UserProfileResource())

urlpatterns = patterns('',
    url(r'^$', 'django_fordrop.views.index', name='index'),
    url(r'^explore/$', 'django_fordrop.views.explore', name='explore'),
    url(r'^welcome/$', 'django_fordrop.views.welcome', name='welcome'),
    url(r'^welcome/(?P<id>[0-9]+)$', 'django_fordrop.views.welcome'),
    url(r'^share/file$', 'django_fordrop.views.file_share', name='share_file'),
    url(r'^search/$', 'django_fordrop.views.search', name='search'),
    url(r'^file/(?P<id>[0-9]+)$', 'django_fordrop.views.file', name='file'),
    url(r'^file/(?P<id>[0-9]+)/comment$', 'django_fordrop.views.file_comment', name='file_comment'),
    url(r'^file/(?P<id>[0-9]+)/tag$', 'django_fordrop.views.file_tag', name='file_tag'),
    url(r'^file/(?P<id>[0-9]+)/clone$', 'django_fordrop.views.file_clone', name='file_clone'),
    url(r'^collection$', 'django_fordrop.views.collection', name='collection'),
    url(r'^collection/(?P<id>[0-9]+)$', 'django_fordrop.views.collection_timeline', name='collection_timeline'),
    url(r'^collection/(?P<id>[0-9]+)/timeline$', 'django_fordrop.views.timeline_json', name='timeline'),
    url(r'^collection/(?P<id>[0-9]+)/comment$', 'django_fordrop.views.collection_comment', name='collection_comment'),
    url(r'^collection/(?P<id>[0-9]+)/tag$', 'django_fordrop.views.collection_tag', name='collection_tag'),
    url(r'^collection/(?P<id>[0-9]+)/follow$', 'django_fordrop.views.collection_follow', name='collection_follow'),
    url(r'^collection/(?P<id>[0-9]+)/unfollow$', 'django_fordrop.views.collection_unfollow', name='collection_unfollow'),
    url(r'^profile/$', 'django_fordrop.views.profile', name='profile'),
    url(r'^profile/(?P<id>[0-9]+)$', 'django_fordrop.views.profile', name='profile'),
    url(r'^profile/edit/$', 'django_fordrop.views.edit_profile', name='edit_profile'),
    url(r'^profile/settings/edit/$', 'django_fordrop.views.edit_settings', name='edit_settings'),
    url(r'^federation/$', 'django_fordrop.views.federation', name='federation'),
    url(r'federation/node/add/$', 'django_fordrop.views.add_pubsub_node', name='add_pubsub_node'),
    url(r'^api/',      include(v1_api.urls)),
    url(r'^accounts/change_password/$',    'django.contrib.auth.views.password_change', {'post_change_redirect' : '/accounts/change_password/done/'}),
    url(r'^accounts/change_password/done/$', 'django.contrib.auth.views.password_change_done'),
    (r'^accounts/', include('registration.backends.default.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    (r'^site_media/(?P<path>.*)$',          'django.views.static.serve', {'document_root': 'fordropweb/fordropweb/static', 'show_indexes': True}),
)
