from django.forms import ModelForm
from apps.pages.models import Page

class PageForm(ModelForm):
    class Meta:
        model = Page
        exclude = ('user')