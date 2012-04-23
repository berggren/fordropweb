from django import forms
from django_fordrop.models import UserProfile, UserSettings
from models import File, FileComment, CollectionComment, Collection

class FileCommentForm(forms.ModelForm):
    class Meta:
        model = FileComment
        fields = ('content',)

class FileTagForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ('tags',)

class CollectionTagForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ('tags',)

class CollectionCommentForm(forms.ModelForm):
    class Meta:
        model = CollectionComment
        fields = ('content',)

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ('title', 'tags', 'description')

class UploadFileForm(forms.ModelForm):
    file = forms.FileField(required=True)
    class Meta:
        model = File
        fields = ('description', 'tags')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'uuid')

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        exclude = ('user')
