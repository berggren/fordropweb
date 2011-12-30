from django.forms import ModelForm
from apps.userprofile.models import UserSettings, UserProfile

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'graph_id')

class UserSettingsForm(ModelForm):
    class Meta:
        model = UserSettings
        exclude = ('user', 'notification_new_follower', 'notification_investigation_post', 'notification_investigation_file', 'notification_investigation_new_investigator')
