from django.contrib.auth.models import User
from tastypie.authorization import Authorization
from tastypie.authentication import ApiKeyAuthentication, Authentication
from tastypie import fields
from tastypie.constants import ALL
from tastypie.resources import ModelResource
from django_fordrop.models import File, FileComment, UserProfile

class UserResource(ModelResource):
    resource_name = 'user'
    class Meta:
        queryset = User.objects.all()
        fields = ['username', 'is_active']
        authorization = Authorization()
        authentication = Authentication()

class FileResource(ModelResource):
    resource_name = 'file'
    user = fields.ForeignKey(UserResource, 'user')
    class Meta:
        queryset = File.objects.all()
        filtering = {
            "uuid": ALL
        }
        authorization = Authorization()
        authentication = Authentication()

class FileCommentResource(ModelResource):
    resource_name = 'filecomment'
    file = fields.ForeignKey(FileResource, 'file', full=True)
    class Meta:
        queryset = FileComment.objects.all()
        authorization = Authorization()
        authentication = Authentication()

class UserProfileResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', full=True)
    class Meta:
        queryset = UserProfile.objects.all()
        excludes = ['id']
        filtering = {
            "uuid": ALL
        }
        authorization = Authorization()
        authentication = Authentication()
