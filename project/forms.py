from django import forms
from .models import Schedule
from django.core.exceptions import ValidationError

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['medicine', 'dosage', 'frequency', 'start_date', 'end_date', 'time']

    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'required': True}),
        label="Time"
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'required': True}),
        label="Start Date"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'required': True}),
        label="End Date"
    )

    def __init__(self, *args, **kwargs):
        """
        Populate the fields with the instance's current values for editing.
        """
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            self.fields['time'].initial = self.instance.time
            self.fields['start_date'].initial = self.instance.start_date
            self.fields['end_date'].initial = self.instance.end_date

    def clean(self):
        """
        Custom validation to ensure end_date is not earlier than start_date.
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise ValidationError("End date cannot be earlier than start date.")

        return cleaned_data
    
class MedicineSearchForm(forms.Form):
    query = forms.CharField(label="Search Medicine", max_length=100)