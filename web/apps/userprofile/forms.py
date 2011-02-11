from django import forms
from fordrop.apps.userprofile.models import * 

class ProfileForm(forms.Form):
    firstname = forms.CharField()
    lastname = forms.CharField()
    email = forms.EmailField()
    #avatar = forms.FileField()