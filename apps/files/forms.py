from django import forms

class UploadFileForm(forms.Form):
    file  = forms.FileField(required=True)
    
class ReferenceForm(forms.Form):
    reference  = forms.CharField()

class SearchForm(forms.Form):
    search = forms.CharField()
    
class TagForm(forms.Form):
    tag = forms.CharField()