from django.db import models
from django.contrib.auth.models import User
import pandas as pd
from django.db.models import Q

class Medicine(models.Model):
    """
    The Medicine model represents individual medicines.
    """
    name = models.CharField(max_length=100, null=True, blank=True)  # Automatically populated
    brand_name = models.CharField(max_length=100, blank=True, null=True)
    generic_name = models.CharField(max_length=100, blank=True, null=True)
    manufacturer = models.CharField(max_length=200, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    dosage_info = models.TextField(blank=True, null=True)
    side_effects = models.TextField(blank=True, null=True)
    purpose = models.TextField(blank=True, null=True)
    indications_and_usage = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.brand_name or "Unknown Medicine"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or "Unknown Medicine"


class UserProfile(models.Model):
    '''
    The UserProfile model extends the default Django User model by adding additional medical-related fields.
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Links to the default Django User model
    first_name = models.CharField(max_length=100, default='') # First name of user
    last_name = models.CharField(max_length=100, default='')
    email = models.EmailField(max_length=254, default='') # Email of the user
    age = models.IntegerField()  # Age of the user
    weight = models.FloatField()  # Weight of the user in kilograms
    allergies = models.TextField()  # List of allergies reported by the user
    medical_conditions = models.TextField()  # List of pre-existing medical conditions

    def __str__(self):
        return self.user.username

class Schedule(models.Model):
    """
    The Schedule model ties a UserProfile to a specific Medicine.
    It represents the schedule for taking a particular medicine, including dosage and timing information.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)  # Links to the medicine being scheduled
    dosage = models.CharField(max_length=100)  # Dosage details
    FREQUENCY_CHOICES = [
        ('once', 'Once (one-time use)'),
        ('daily', 'Daily'),
        ('twice_daily', 'Twice Daily'),
        ('every_4_hours', 'Every 4 hours'),
        ('every_8_hours', 'Every 8 hours'),
        ('weekly', 'Weekly'),
        ('every_other_day', 'Every Other Day'),
    ]
    frequency = models.CharField(
        max_length=50,
        choices=FREQUENCY_CHOICES,
        default='daily'  # Default to 'Daily'
    )  # Frequency
    start_date = models.DateField()  # Start date for taking the medicine
    end_date = models.DateField()  # End date for taking the medicine
    time = models.TimeField()  # Time for taking the medicine

    def __str__(self):
        return f"{self.medicine.name} scheduled for {self.frequency}"

class Interaction(models.Model):
    """
    The Interaction model describes potential interactions between two medicines.
    It includes details of the interaction and its severity level.
    """
    medicine1 = models.ForeignKey(Medicine, related_name='interaction1', on_delete=models.CASCADE)  # First medicine
    medicine2 = models.ForeignKey(Medicine, related_name='interaction2', on_delete=models.CASCADE)  # Second medicine
    interaction_type = models.CharField(max_length=100, default='n/a')  # Type of interaction 
    description = models.TextField()  # Description of the interaction 
    severity_level = models.CharField(max_length=100)  # Severity level
    

    def __str__(self):
        return f"Interaction between {self.medicine1.name} and {self.medicine2.name}"

# Function to ensure interaction exists or is updated
def ensure_interaction(medicine1_name, medicine2_name, interaction_type=None, description=None, severity_level=None):
    """
    Ensure that an interaction between two medicines exists, updating or creating as needed.
    Handles deduplication by considering both (medicine1, medicine2) and (medicine2, medicine1).
    """
    try:
        # Retrieve Medicine objects
        medicine1 = Medicine.objects.get(name=medicine1_name)
        medicine2 = Medicine.objects.get(name=medicine2_name)

        # Check if interaction already exists (in either order)
        interaction = Interaction.objects.filter(
            Q(medicine1=medicine1, medicine2=medicine2) |
            Q(medicine1=medicine2, medicine2=medicine1)
        ).first()

        if interaction:
            # Update the existing interaction with new details if provided
            if interaction_type and not interaction.interaction_type:
                interaction.interaction_type = interaction_type
            if description and not interaction.description:
                interaction.description = description
            if severity_level and not interaction.severity_level:
                interaction.severity_level = severity_level
            interaction.save()
            print(f'Updated interaction: {interaction}')
        else:
            # Create a new interaction
            interaction = Interaction(
                medicine1=medicine1,
                medicine2=medicine2,
                interaction_type=interaction_type or "N/A",
                description=description or "N/A",
                severity_level=severity_level or "N/A"
            )
            interaction.save()
            print(f'Created new interaction: {interaction}')

    except Medicine.DoesNotExist as e:
        print(f'Medicine not found: {e}')
    except Exception as e:
        print(f'Error ensuring interaction: {e}')

def load_ddi_data():
    """
    Load interaction data from ddi_data.csv
    """
    file_path = r'C:\Users\jiany\downloads\school\django\data\ddi_data.csv'

    # Clear existing Interaction records
    Interaction.objects.all().delete()

    try:
        # Read the CSV file using pandas
        ddi_data = pd.read_csv(file_path)

        # Iterate over the rows and create/update Interaction records
        for _, row in ddi_data.iterrows():
            try:
                # Ensure medicine1 exists or create it
                medicine1, _ = Medicine.objects.get_or_create(name=row['drug1_name'])

                # Ensure medicine2 exists or create it
                medicine2, _ = Medicine.objects.get_or_create(name=row['drug2_name'])

                # Use ensure_interaction to create or update interactions
                ensure_interaction(
                    medicine1_name=medicine1.name,
                    medicine2_name=medicine2.name,
                    interaction_type=row['interaction_type']
                )
            except Exception as e:
                print(f'Error processing row {row}: {e}')
    except Exception as e:
        print(f'Error reading file {file_path}: {e}')

def load_db_drug_interactions():
    """
    Load interaction data from db_drug_interactions.csv
    """
    file_path = r'C:\Users\jiany\downloads\school\django\data\db_drug_interactions.csv'

    try:
        # Read the CSV file using pandas
        db_drug_interactions = pd.read_csv(file_path)

        # Iterate over the rows and create/update Interaction records
        for _, row in db_drug_interactions.iterrows():
            try:
                # Ensure medicine1 exists or create it
                medicine1, _ = Medicine.objects.get_or_create(name=row['Drug 1'])

                # Ensure medicine2 exists or create it
                medicine2, _ = Medicine.objects.get_or_create(name=row['Drug 2'])

                # Use ensure_interaction to create or update interactions
                ensure_interaction(
                    medicine1_name=medicine1.name,
                    medicine2_name=medicine2.name,
                    description=row['Interaction Description']
                )
            except Exception as e:
                print(f'Error processing row {row}: {e}')
    except Exception as e:
        print(f'Error reading file {file_path}: {e}')

def load_ddinter_files(file_paths):
    """
    Load interaction data from multiple ddinter_downloads_code_*.csv files
    """

    for file_path in file_paths:
        print(f'Processing file: {file_path}')
        try:
            # Read the CSV file using pandas
            ddinter_data = pd.read_csv(file_path)

            # Iterate over the rows and create/update Interaction records
            for _, row in ddinter_data.iterrows():
                try:
                    # Ensure medicine1 exists or create it
                    medicine1, _ = Medicine.objects.get_or_create(name=row['Drug_A'])

                    # Ensure medicine2 exists or create it
                    medicine2, _ = Medicine.objects.get_or_create(name=row['Drug_B'])

                    # Use ensure_interaction to create or update interactions
                    ensure_interaction(
                        medicine1_name=medicine1.name,
                        medicine2_name=medicine2.name,
                        interaction_type=row['Level']
                    )
                except Exception as e:
                    print(f'Error processing row {row}: {e}')
        except Exception as e:
            print(f'Error reading file {file_path}: {e}')

    print("Completed loading ddinter data.")
