from django import forms
from models import *

class NewInvestigationForm(forms.Form):
    title = forms.CharField()
    
class InvestigationForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea)

class FooInvestigationForm(forms.Form):
    title = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)
    status = forms.ModelChoiceField(queryset=Status.objects.all())
    reference = forms.ModelChoiceField(queryset=Reference.objects.all())