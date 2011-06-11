from django import forms
from apps.userprofile.models import * 

class ProfileForm(forms.Form):
    firstname = forms.CharField()
    lastname = forms.CharField()
    email = forms.EmailField()
    #avatar = forms.FileField()
