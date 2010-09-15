from django import forms
from models import *

class NewInvestigationForm(forms.Form):
    title = forms.CharField()