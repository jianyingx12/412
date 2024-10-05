from django.db import models

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