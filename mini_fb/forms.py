from django import forms
from .models import Profile, StatusMessage

class CreateProfileForm(forms.ModelForm):
    '''A form to add a profile to the database'''
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'city', 'bio', 'email', 'profile_image_url']

class CreateStatusMessageForm(forms.ModelForm):
    '''A form to add a statusmessage on an profile to the database'''
    class Meta:
        model = StatusMessage
        fields = ['message']
        labels = {
            'message': 'Message',
        }

class UpdateProfileForm(forms.ModelForm):
    '''A form to update a profile, excluding first name and last name'''
    
    class Meta:
        model = Profile
        fields = ['city', 'bio', 'email', 'profile_image_url']
        