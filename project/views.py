from django.views.generic import ListView, CreateView, TemplateView, DeleteView
from django.shortcuts import redirect
from django.urls import reverse
from .models import Medicine, Schedule, Interaction
from .forms import ScheduleForm  
from datetime import timedelta, date
from django.utils.timezone import now
import requests
from django.shortcuts import render
from .forms import MedicineSearchForm
from django.contrib import messages

# Medicine List View
class MedicineListView(ListView):
    """
    Displays all medicines stored in the database.
    """
    model = Medicine
    template_name = 'project/medicines.html'  # Template for the medicine list
    context_object_name = 'medicines'  # Variable to use in the template


# Add Medicine to Schedule View
class ScheduleCreateView(CreateView):
    """
    Allows users to add a medicine to the schedule using a form.
    """
    model = Schedule
    form_class = ScheduleForm
    template_name = 'project/add_schedule.html'  # Template for the form
    success_url = '/schedules/'  # Redirect URL after successful submission

    def form_valid(self, form):
        """
        For now, leave the user_profile association blank.
        """
        # Commented out user association until user handling is added
        # form.instance.user_profile = self.request.user.userprofile
        return super().form_valid(form)

# Drug Interaction Check View
class InteractionCheckView(TemplateView):
    """
    Checks for potential interactions between scheduled medicines.
    """
    template_name = 'project/interactions.html'

    def get_context_data(self, **kwargs):
        """
        Adds interaction data to the context for rendering in the template.
        """
        context = super().get_context_data(**kwargs)
        schedules = Schedule.objects.all()  # For now, fetch all schedules
        interactions = []

        for schedule1 in schedules:
            for schedule2 in schedules:
                if schedule1.medicine != schedule2.medicine:
                    interaction = Interaction.objects.filter(
                        medicine1=schedule1.medicine,
                        medicine2=schedule2.medicine
                    ).first()
                    if interaction:
                        interactions.append(interaction)

        context['interactions'] = interactions
        return context


# Weekly Schedule View
class ScheduleView(TemplateView):
    template_name = 'project/schedule.html'

    def get_context_data(self, **kwargs):
        """
        Add the user's weekly schedule and navigation dates to the context.
        """
        context = super().get_context_data(**kwargs)

        # Get the current week or a specific week from query parameters
        week_start = self.request.GET.get('week_start')
        if week_start:
            try:
                week_start = date.fromisoformat(week_start)  # Parse date from query string
            except ValueError:
                week_start = now().date()  # Default to current date if invalid
        else:
            today = now().date()
            # Calculate the most recent Sunday
            week_start = today - timedelta(days=(today.weekday() + 1) % 7)

        # Calculate the end of the week (Saturday)
        week_end = week_start + timedelta(days=6)

        # Calculate previous and next weeks for navigation
        context['previous_week'] = week_start - timedelta(days=7)
        context['next_week'] = week_start + timedelta(days=7)

        # Filter schedules for the selected week
        schedules = Schedule.objects.filter(
            start_date__lte=week_end,  # Schedules that started before the end of the week
            end_date__gte=week_start  # Schedules that end after the start of the week
        ).order_by('time')

        # Organize schedules by day of the week
        days_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        weekly_schedule = {day: [] for day in days_of_week}

        for schedule in schedules:
            # Calculate the day of the week for the schedule based on start_date
            schedule_day_index = (schedule.start_date - week_start).days
            if 0 <= schedule_day_index <= 6:  # Ensure it falls within the week range
                day_name = days_of_week[schedule_day_index]
                weekly_schedule[day_name].append(schedule)

        context['weekly_schedule'] = weekly_schedule
        context['week_start'] = week_start
        context['week_end'] = week_end
        return context
    
class MedicineDetailView(TemplateView):
    template_name = 'project/medicine_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['medicine'] = self.request.GET.dict()  # Pass all details as context
        return context

class MedicineDetailFromListView(TemplateView):
    template_name = 'project/medicine_detail_from_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medicine_id = self.request.GET.get('id')  # Get the medicine ID from the URL query parameter
        try:
            medicine = Medicine.objects.get(id=medicine_id)
            context['medicine'] = medicine
        except Medicine.DoesNotExist:
            context['medicine'] = None
        return context

class MedicineDeleteView(DeleteView):
    """
    Handles the deletion of a Medicine instance.
    """
    model = Medicine
    template_name = 'project/medicine_confirm_delete.html'  # Confirmation page

    def get_success_url(self):
        """
        Redirects to the list of medicines after deletion.
        """
        return reverse('medicines')

class MedicineSearchView(TemplateView):
    template_name = 'project/medicine_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MedicineSearchForm()
        return context

    def post(self, request):
        form = MedicineSearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']

            BASE_URL = "https://api.fda.gov/drug/label.json"
            params = {
                "search": f'openfda.brand_name:"{query}" OR openfda.generic_name:"{query}"',
                "limit": 15
            }

            try:
                response = requests.get(BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])

                medicines = []
                for result in results:
                    medicine_info = {
                        "brand_name": result.get("openfda", {}).get("brand_name", ["N/A"])[0],
                        "manufacturer": result.get("openfda", {}).get("manufacturer_name", ["N/A"])[0],
                        "details": {  # Details for the view details button
                            "brand_name": result.get("openfda", {}).get("brand_name", ["N/A"])[0],
                            "generic_name": result.get("openfda", {}).get("generic_name", ["N/A"])[0],
                            "manufacturer": result.get("openfda", {}).get("manufacturer_name", ["N/A"])[0],
                            "category": result.get("openfda", {}).get("pharmacologic_class", ["N/A"])[0],
                            "dosage_info": result.get("dosage_and_administration", ["N/A"])[0],
                            "side_effects": result.get("adverse_reactions", ["N/A"])[0] or result.get("warnings_and_precautions", ["N/A"])[0],
                            "purpose": result.get("purpose", ["N/A"])[0],
                            "indications_and_usage": result.get("indications_and_usage", ["N/A"])[0],
                        }
                    }
                    medicines.append(medicine_info)

                return render(request, self.template_name, {'form': form, 'medicines': medicines})
            except requests.exceptions.RequestException as e:
                return render(request, self.template_name, {'form': form, 'error': f"An error occurred: {str(e)}"})
        else:
            return render(request, self.template_name, {'form': form, 'error': 'Invalid input. Please try again.'})
        
def add_to_medicines(request):
    """
    Adds a new medicine to the database from the GET request parameters.
    """
    if request.method == "GET":
        brand_name = request.GET.get("brand_name")
        generic_name = request.GET.get("generic_name")
        manufacturer = request.GET.get("manufacturer")
        category = request.GET.get("category")
        dosage_info = request.GET.get("dosage_info")
        side_effects = request.GET.get("side_effects")
        purpose = request.GET.get("purpose")
        indications_and_usage = request.GET.get("indications_and_usage")

        # Avoid duplicate entries by checking if it already exists
        if Medicine.objects.filter(brand_name=brand_name).exists():
            messages.warning(request, "This medicine is already in the database.")
        else:
            # Add the medicine to the database
            Medicine.objects.create(
                brand_name=brand_name,
                generic_name=generic_name,
                manufacturer=manufacturer,
                category=category,
                indications_and_usage=indications_and_usage,  
                dosage_info=dosage_info,
                side_effects=side_effects,
                purpose=purpose,
            )
            messages.success(request, f"Medicine '{brand_name}' added successfully!")

        return redirect("medicines")  # Redirect to the medicine list