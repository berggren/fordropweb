from django import forms
from django.forms import ModelForm
from apps.report.models import File

class TagForm(ModelForm):
    class Meta:
        model = File
        fields = ('tags',)

class UploadFileForm(forms.Form):
    file  = forms.FileField(required=True)

class DescriptionForm(ModelForm):
    class Meta:
        model = File
    fields = ('description')
