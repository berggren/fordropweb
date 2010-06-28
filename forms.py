from django import forms
    
class TagForm(forms.Form):
    tag = forms.CharField()

class ReferenceForm(forms.Form):
    reference  = forms.CharField()