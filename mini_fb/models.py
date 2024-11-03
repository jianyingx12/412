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
    
    def get_friends(self):
        # Retrieve all Friend relationships where self is either profile1 or profile2
        friends = Friend.objects.filter(
            models.Q(profile1=self) | models.Q(profile2=self)
        )

        # Extract the other profile from each Friend relationship
        friend_profiles = [
            friend.profile1 if friend.profile2 == self else friend.profile2
            for friend in friends
        ]

        return friend_profiles
    
    def add_friend(self, other):
        # Check for self-friending
        if self == other:
            return

        # Check if a Friend relationship already exists
        existing_friend = Friend.objects.filter(
            models.Q(profile1=self, profile2=other) | models.Q(profile1=other, profile2=self)
        ).exists()
        
        if not existing_friend:
            # Create the Friend relationship
            Friend.objects.create(profile1=self, profile2=other)

    def get_friend_suggestions(self):
        # Get all profiles except self
        possible_friends = Profile.objects.exclude(pk=self.pk)

        # Exclude current friends
        friends = self.get_friends()  
        friend_ids = [friend.pk for friend in friends]
        suggestions = possible_friends.exclude(pk__in=friend_ids)

        return suggestions
    
    def get_news_feed(self):
        # Get all friends' profiles
        friend_profiles = self.get_friends()

        # Combine self and friends' status messages
        news_feed = StatusMessage.objects.filter(
            models.Q(profile=self) | models.Q(profile__in=friend_profiles)
        ).order_by('-timestamp')

        return news_feed

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
    
class Friend(models.Model):
    '''
    Encapsulate the idea of befriending others
    '''

    # First profile in the friendship
    profile1 = models.ForeignKey('Profile', related_name="profile1", on_delete=models.CASCADE)
    # Second profile in the friendship
    profile2 = models.ForeignKey('Profile', related_name="profile2", on_delete=models.CASCADE)
    # Timestamp of when the friendship was created
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.profile1} & {self.profile2}"