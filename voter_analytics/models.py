from django.db import models
import csv
from datetime import datetime

# Create your models here.

class Voter(models.Model):
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    street_number = models.CharField(max_length=10)
    street_name = models.CharField(max_length=100)
    apartment_number = models.CharField(max_length=10, blank=True, null=True)
    zip_code = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    date_of_registration = models.DateField()
    party_affiliation = models.CharField(max_length=30)
    precinct_number = models.CharField(max_length=10)
    v20state = models.BooleanField()
    v21town = models.BooleanField()
    v21primary = models.BooleanField()
    v22general = models.BooleanField()
    v23town = models.BooleanField()
    voter_score = models.IntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.party_affiliation})"
    


def load_data():
    # Filepath to csv
    file_path = 'C:/Users/jiany/downloads/newton_voters.csv'

    # Clear existing records 
    Voter.objects.all().delete()

    # Open the CSV file for reading
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:

                # Helper function to parse boolean values from strings
                def parse_bool(value):
                    return value.strip().upper() == 'TRUE'

                # Create a new Voter object with data from the CSV row
                voter = Voter(
                    last_name=row['Last Name'],
                    first_name=row['First Name'],
                    street_number=row['Residential Address - Street Number'],
                    street_name=row['Residential Address - Street Name'],
                    apartment_number=row.get('Residential Address - Apartment Number'),
                    zip_code=row['Residential Address - Zip Code'],
                    date_of_birth=datetime.strptime(row['Date of Birth'], '%Y-%m-%d').date(),
                    date_of_registration=datetime.strptime(row['Date of Registration'], '%Y-%m-%d').date(),
                    party_affiliation=row['Party Affiliation'],
                    precinct_number=row['Precinct Number'],
                    v20state=parse_bool(row['v20state']),
                    v21town=parse_bool(row['v21town']),
                    v21primary=parse_bool(row['v21primary']),
                    v22general=parse_bool(row['v22general']),
                    v23town=parse_bool(row['v23town']),
                    voter_score=int(row['voter_score'])
                )
                voter.save()
                print(f'Created voter: {voter}')
            except Exception as e:
                print(f'Error processing row {row}: {e}')
