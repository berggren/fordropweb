from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.authentication import ApiKeyAuthentication, Authentication
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from tastypie.constants import ALL
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from apps.report.models import File
from apps.boxes.models import Box
from apps.userprofile.models import UserProfile
from apps.post.models import Post
from src.apps.post.models import NewPost

class HeaderApiKeyAuthentication(ApiKeyAuthentication):
    def is_authenticated(self, request, **kwargs):
        username = request.META.get('HTTP_X_FORDROP_USERNAME') or request.GET.get('username')
        api_key = request.META.get('HTTP_X_FORDROP_API_KEY') or request.GET.get('api_key')
        if not username or not api_key:
            return self._unauthorized()
        try:
            user = User.objects.get(username=username)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return self._unauthorized()
        request.user = user
        return self.get_key(user, api_key)



class ProfileResource(ModelResource):
    class Meta:
        queryset = UserProfile.objects.all()
        resource_name = 'profile'
        authorization = Authorization()
        authentication = HeaderApiKeyAuthentication()

class UserResource(ModelResource):
    profile = fields.ForeignKey(ProfileResource, 'profile', full=True)
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        authorization = Authorization()
        authentication = HeaderApiKeyAuthentication()
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']
        filtering = {
            "username": ALL
        }

class BareUserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'bare_user'
        authorization = Authorization()
        authentication = HeaderApiKeyAuthentication()
        excludes = ['email', 'password', 'is_staff', 'is_superuser']

class BoxResource(ModelResource):
    class Meta:
        queryset = Box.objects.all()
        resource_name = 'box'
        allowed_methods = ['get', 'put', 'post']
        authorization = Authorization()
        authentication = HeaderApiKeyAuthentication()

class PostResource(ModelResource):
    author = fields.ForeignKey(BareUserResource, 'author', full=True)
    boxes = fields.ToManyField(BoxResource, 'boxes', full=True)
    class Meta:
        queryset = NewPost.objects.all()
        resource_name = 'post'
        authorization = Authorization()
        authentication = HeaderApiKeyAuthentication()
        filtering = {
            "published": ALL,
            "uuid": ALL
        }

class FullPostResource(ModelResource):
    author = fields.ForeignKey(UserResource, 'author', full=True)
    boxes = fields.ToManyField(BoxResource, 'boxes', full=True)
    class Meta:
        queryset = NewPost.objects.all()
        resource_name = 'full_post'
        authorization = Authorization()
        authentication = HeaderApiKeyAuthentication()
        filtering = {
            "published": ALL,
            "uuid": ALL
        }

class FileResource(ModelResource):
    user = fields.ForeignKey(BareUserResource, 'user', full=True)
    boxes = fields.ToManyField(BoxResource, 'boxes', full=True)
    class Meta:
        queryset = File.objects.all()
        resource_name = 'file'
        allowed_methods = ['get', 'put', 'post']
        authorization = Authorization()
        authentication = HeaderApiKeyAuthentication()
        filtering = {
            "published": ALL,
            "uuid": ALL
        }

class FullFileResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', full=True)
    boxes = fields.ToManyField(BoxResource, 'boxes', full=True)
    class Meta:
        queryset = File.objects.all()
        resource_name = 'full_file'
        allowed_methods = ['get', 'put', 'post']
        authorization = Authorization()
        authentication = HeaderApiKeyAuthentication()
        filtering = {
            "published": ALL,
            "uuid": ALL
        }
