from django import forms
    
class TagForm(forms.Form):
    tag = forms.CharField()
