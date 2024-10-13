from django.db import models
from django.utils import timezone

# Create your models here.

class Profile(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    profile_image_url = models.URLField(max_length=200)

    def __str__(self):
        '''Return a string representation of this object.'''
        return f'{self.first_name} {self.last_name}'
    
    def get_status_messages(self):
        '''Return a QuerySet of all status messages for this profile.'''

        messages = StatusMessage.objects.filter(profile=self).order_by('-timestamp')
        return messages

class StatusMessage(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    message = models.TextField()
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='status_messages')

    def __str__(self):
        return f'Status by {self.profile.first_name} at {self.timestamp}: {self.message}'
