from django.db import models
from django.utils import timezone
from django.urls import reverse

# Create your models here.

class Profile(models.Model):
    '''Encapsulate the idea of one profile'''
    # data attributes of an Article:
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    bio = models.CharField(max_length=500, blank=True, null=True)
    email = models.EmailField(max_length=254)
    profile_image_url = models.URLField()

    def __str__(self):
        '''Return a string representation of this object.'''
        return f'{self.first_name} {self.last_name}'
    
    def get_status_messages(self):
        '''Return a QuerySet of all status messages for this profile.'''

        messages = StatusMessage.objects.filter(profile=self).order_by('-timestamp')
        return messages
    
    def get_absolute_url(self):
        return reverse('show_profile', kwargs={'pk': self.pk})

class StatusMessage(models.Model):
    '''
    Encapsulate the idea of a status message on a profile.
    '''

    # model the 1 to many relationship with profile (foreign key)
    timestamp = models.DateTimeField(default=timezone.now)
    message = models.TextField()
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='status_messages')

    def __str__(self):
        return f'Status by {self.profile.first_name} at {self.timestamp}: {self.message}'
    
    def get_images(self):
        '''Return all images associated with this status message.'''
        return self.images.all()  # 'images' is the related_name from the Image model
    
class Image(models.Model):
    '''
    Encapsulate the idea of an image file that is uploaded and related to a status message.
    '''
    
    # ForeignKey linking to StatusMessage
    status_message = models.ForeignKey('StatusMessage', on_delete=models.CASCADE, related_name='images')
    
    # Image field to upload image files
    image_file = models.ImageField(blank=True)  
    
    # Timestamp of when the image was uploaded
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f'Image for StatusMessage {self.status_message.id} at {self.timestamp}'
