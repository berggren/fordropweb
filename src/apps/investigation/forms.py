from django.forms import ModelForm
from apps.investigation.models import Investigation

class TagForm(ModelForm):
    class Meta:
        model = Investigation
        fields = ('tags',)
