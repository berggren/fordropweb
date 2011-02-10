from django import forms
from models import *

class GenericReportForm(forms.Form):
    type = forms.ModelChoiceField(queryset=TypeReport.objects.all())
    value = forms.CharField()