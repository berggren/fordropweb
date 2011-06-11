from django import forms

class UploadFileForm(forms.Form):
    file  = forms.FileField(required=True)

class GenericReportForm(forms.Form):
    value = forms.CharField()

class TagForm(forms.Form):
    tag = forms.CharField()

class ReferenceForm(forms.Form):
    reference  = forms.CharField()

