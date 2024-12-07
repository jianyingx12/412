from django import forms
from .models import Schedule

class ScheduleForm(forms.ModelForm):
    """
    A form for creating and editing Schedule instances.
    Allows users to specify details for scheduling a medicine.
    """
    class Meta:
        model = Schedule  # Links the form to the Schedule model
        fields = [
            'medicine',       # The medicine being scheduled
            'dosage',         # The dosage of the medicine 
            'frequency',      # The frequency of administration
            'start_date',     # The date when the user starts taking the medicine
            'end_date',       # The date when the user stops taking the medicine
            'time',           # The specific time of day to take the medicine
        ]

class MedicineSearchForm(forms.Form):
    query = forms.CharField(label="Search Medicine", max_length=100)