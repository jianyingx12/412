from django.db import models
from django.contrib.auth.models import User

class Medicine(models.Model):
    '''
    The Medicine model represents individual medicines. 
    '''
    name = models.CharField(max_length=100)  # Name of the medicine (e.g., Ibuprofen, Warfarin)
    category = models.CharField(max_length=100)  # Category of the medicine (e.g., NSAID, anticoagulant)
    common_uses = models.TextField()  # Text description of common uses (e.g., pain relief, blood thinning)
    dosage_info = models.TextField()  # Information about standard dosage
    side_effects = models.TextField()  # Information about possible side effects

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    '''
    The UserProfile model extends the default Django User model by adding additional medical-related fields.
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Links to the default Django User model
    age = models.IntegerField()  # Age of the user
    weight = models.FloatField()  # Weight of the user in kilograms
    allergies = models.TextField()  # List of allergies reported by the user
    medical_conditions = models.TextField()  # List of pre-existing medical conditions

    def __str__(self):
        return self.user.username

class Schedule(models.Model):
    '''
    The Schedule model ties a UserProfile to a specific Medicine.
    It represents the schedule for taking a particular medicine, including dosage and timing information.
    '''
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)  # Links to the user's profile
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)  # Links to the medicine being scheduled
    dosage = models.CharField(max_length=100)  # Dosage details 
    frequency = models.CharField(max_length=100)  # Frequency 
    start_date = models.DateField()  # Start date for taking the medicine
    end_date = models.DateField()  # End date for taking the medicine
    time = models.TimeField()  # Time for taking the medicine

    def __str__(self):
        return f"{self.medicine.name} for {self.user_profile.user.username}"



class Interaction(models.Model):
    '''
    The Interaction model describes potential interactions between two medicines.
    It includes details of the interaction and its severity level.
    '''
    medicine1 = models.ForeignKey(Medicine, related_name='interaction1', on_delete=models.CASCADE)  # First medicine
    medicine2 = models.ForeignKey(Medicine, related_name='interaction2', on_delete=models.CASCADE)  # Second medicine
    description = models.TextField()  # Description of the interaction (e.g., "Increased risk of bleeding")
    severity_level = models.CharField(max_length=100)  # Severity level

    def __str__(self):
        return f"Interaction between {self.medicine1.name} and {self.medicine2.name}"
