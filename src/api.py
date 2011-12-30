from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.authentication import ApiKeyAuthentication
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from tastypie.constants import ALL
from apps.report.models import File

class FileResource(ModelResource):
    class Meta:
        queryset = File.objects.all()
        resource_name = 'file'
        allowed_methods = ['get', 'put', 'post']
        authorization = Authorization()
        authentication = ApiKeyAuthentication()
        filtering = {
            "published": ALL
        }
