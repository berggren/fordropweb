from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.authentication import ApiKeyAuthentication, Authentication
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from tastypie.constants import ALL
from django.contrib.auth.models import User
from apps.report.models import File
from apps.pages.models import Page
from apps.boxes.models import Box

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'

class PageResource(ModelResource):
    class Meta:
        queryset = Page.objects.all()
        resource_name = 'page'

class BoxResource(ModelResource):
    class Meta:
        queryset = Box.objects.all()
        resource_name = 'box'
        authorization = Authorization()
        authentication = Authentication()
        allowed_methods = ['get', 'put', 'post']

class FileResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    boxes = fields.ToManyField(BoxResource, 'boxes', full=True)
    class Meta:
        queryset = File.objects.all()
        resource_name = 'file'
        allowed_methods = ['get', 'put', 'post']
        authorization = Authorization()
        authentication = ApiKeyAuthentication()
        filtering = {
            "published": ALL
        }
