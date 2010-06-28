from django import forms

class PhishingForm(forms.Form):
    phish = forms.CharField()

class ReferenceForm(forms.Form):
    reference  = forms.CharField()