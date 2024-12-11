from django.views.generic import ListView, CreateView, TemplateView, DeleteView, UpdateView, DetailView, View
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse
from .models import Medicine, Schedule, Interaction
from .forms import ScheduleForm  
from datetime import timedelta, date, datetime
from django.utils.timezone import now
import requests
from django.shortcuts import render
from .forms import MedicineSearchForm
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from .forms import CreateProfileForm, UpdateProfileForm
from django.urls import reverse_lazy
from .models import UserProfile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpRequest
from typing import Any

class ViewProfileView(LoginRequiredMixin, DetailView):
    """
    View to display the user's profile.
    """
    model = UserProfile
    template_name = 'project/view_profile.html'  # Template for displaying the profile

    def get_object(self, queryset=None):
        """
        Ensure the user can only view their own profile.
        """
        return self.request.user.userprofile

class UpdateProfileView(LoginRequiredMixin, UpdateView):
    """
    View to update a user's profile.
    """
    model = UserProfile
    form_class = UpdateProfileForm
    template_name = 'project/update_profile.html'  # Template for the form

    def get_object(self, queryset=None):
        """
        Ensure the user can only edit their own profile.
        """
        return self.request.user.userprofile

    def form_valid(self, form):
        """
        Redirect to the profile page after successfully updating.
        """
        form.save()
        return redirect('project_home')

class InteractionListView(ListView):
    """
    Displays all interactions stored in the database with pagination.
    """
    model = Interaction
    template_name = 'project/interactions.html'  # Specify the template to render
    context_object_name = 'interactions'  # Name of the context variable in the template
    paginate_by = 50  # Number of interactions per page

class UserLoginView(LoginView):
    """
    View to handle user login.
    """
    template_name = 'project/login.html'

    def get_success_url(self):
        """
        Redirect to the home page after successful login.
        """
        return reverse_lazy('project_home')

class CreateProfileView(CreateView):
    '''Create a profile'''
    form_class = CreateProfileForm
    template_name = 'project/create_profile.html'

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        '''Handle the user creation and profile form submission.'''

        # Check if it's an HTTP POST request
        if request.method == 'POST':
            # Reconstruct the UserCreationForm from POST data
            user_form = UserCreationForm(request.POST)

            # If the UserCreationForm is not valid, display errors
            if not user_form.is_valid():
                print(f"user_form.errors={user_form.errors}")
                return self.render_to_response(self.get_context_data(user_form=user_form))

            # Save the user and log them in
            user = user_form.save()
            login(request, user)
            print(f"CreateProfileView.dispatch: {user} is logged in.")

            # Proceed to create profile using the logged-in user
            return super().dispatch(request, *args, **kwargs)

        # If it's a GET request, let the superclass handle it
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict:
        '''Provide context data including UserCreationForm.'''
        # Call the superclass's get_context_data to ensure existing context is included
        context = super().get_context_data(**kwargs)

        # Check if a 'user_form' instance is provided in kwargs, otherwise use a default UserCreationForm instance
        # This ensures that validation errors or previously filled data can be passed back to the form in the template
        context['user_form'] = kwargs.get('user_form', UserCreationForm())

        # Return the modified context dictionary
        return context


    def form_valid(self, form):
        '''Process both the User and Profile forms on valid submission.'''

        # Since we are logged in at this point, get the current user
        user = self.request.user

        # Attach the user to the Profile instance
        form.instance.user = user
        print(f'CreateProfileView.form_valid: Creating profile for user {user.username}')

        # Save the Profile and proceed with the superclass's handling
        return super().form_valid(form)

    def get_success_url(self):
        '''Redirect to the home page after successful profile creation.'''
        return reverse('project_home')

# Medicine List View
class MedicineListView(ListView):
    """
    Displays all medicines stored in the database of the user with pagination.
    """
    model = Medicine
    template_name = 'project/medicines.html'  # Template for the medicine list
    context_object_name = 'medicines'  # Variable to use in the template
    paginate_by = 100 # pagination by 100

# Add Medicine to Schedule View
class ScheduleCreateView(CreateView):
    """
    Allows users to add a medicine to the schedule using a form.
    """
    model = Schedule
    form_class = ScheduleForm
    template_name = 'project/add_to_schedule.html'  # Template for the form
    success_url = '/project/'  # Redirect URL after successful submission

    def form_valid(self, form):
        """
        Handle the form validation and create multiple schedule entries based on the frequency.
        """
        schedule = form.save(commit=False)

        # Extract relevant data
        start_date = schedule.start_date
        end_date = schedule.end_date
        time = schedule.time
        frequency = schedule.frequency
        medicine = schedule.medicine
        dosage = schedule.dosage

        # Map frequency to interval
        interval_map = {
            'once': None,
            'daily': timedelta(days=1),
            'twice_daily': timedelta(hours=12),
            'every_4_hours': timedelta(hours=4),
            'every_8_hours': timedelta(hours=8),
            'weekly': timedelta(weeks=1),
            'every_other_day': timedelta(days=2),
        }

        interval = interval_map.get(frequency)

        if not interval and frequency != 'once':
            raise ValueError(f"Invalid frequency: {frequency}")

        # Prepare schedule entries
        schedules = []

        current_datetime = datetime.combine(start_date, time)
        end_datetime = datetime.combine(end_date, time)

        while current_datetime <= end_datetime:
            # Check if a schedule already exists for this date and time
            if not Schedule.objects.filter(
                medicine=medicine,
                time=current_datetime.time(),
                start_date=current_datetime.date()
            ).exists():
                schedules.append(Schedule(
                    medicine=medicine,
                    dosage=dosage,
                    frequency=frequency,
                    start_date=current_datetime.date(),
                    end_date=end_date,  # Store the original end date
                    time=current_datetime.time()
                ))

            # Increment the datetime
            if frequency == 'once':
                break
            elif frequency == 'twice_daily' and current_datetime.time() == time:
                # Handle the second time for twice daily
                current_datetime += timedelta(hours=12)
            else:
                current_datetime += interval

            # Reset time to initial if daily
            if frequency == 'daily' and current_datetime.time() != time:
                current_datetime = datetime.combine(current_datetime.date(), time)

        # Bulk create the schedules
        Schedule.objects.bulk_create(schedules)

        return redirect(self.success_url)

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
    """
    Renders the details of a medicine passed as query parameters in the URL.
    """
    template_name = 'project/medicine_detail.html'

    def get_context_data(self, **kwargs):
        """
        Adds all query parameters from the GET request as context data for the template.

        This is useful when details are passed directly via the URL query string.
        """
        # Call the superclass's get_context_data to ensure existing context is included
        context = super().get_context_data(**kwargs)

        # Pass all query parameters as a dictionary to the template under the 'medicine' key
        context['medicine'] = self.request.GET.dict()

        return context


class MedicineDetailFromListView(TemplateView):
    """
    Renders the details of a medicine retrieved from the database by its ID.
    """
    template_name = 'project/medicine_detail_from_list.html'

    def get_context_data(self, **kwargs):
        """
        Fetches the medicine details based on the medicine ID passed in the URL query string.
        
        If the medicine exists in the database, it is added to the context.
        If not, 'medicine' is set to None.
        """
        # Call the superclass's get_context_data to ensure existing context is included
        context = super().get_context_data(**kwargs)

        # Retrieve the medicine ID from the query parameter in the URL
        medicine_id = self.request.GET.get('id')

        try:
            # Attempt to fetch the medicine with the given ID from the database
            medicine = Medicine.objects.get(id=medicine_id)
            context['medicine'] = medicine  # Add the medicine object to the context
        except Medicine.DoesNotExist:
            # Handle cases where the medicine does not exist by setting 'medicine' to None
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
    # Specifies the template to render for the view
    template_name = 'project/medicine_search.html'

    def get_context_data(self, **kwargs):
        # Adds additional context data to the template (e.g., form instance)
        context = super().get_context_data(**kwargs)
        context['form'] = MedicineSearchForm()  # Initializes an empty form for the GET request
        return context

    def post(self, request):
        # Handles the POST request when the form is submitted
        form = MedicineSearchForm(request.POST)  # Bind the submitted data to the form
        if form.is_valid():  # Check if the submitted form data is valid
            query = form.cleaned_data['query']  # Retrieve the user's search query

            # API base URL for querying medicine data
            BASE_URL = "https://api.fda.gov/drug/label.json"
            params = {
                "search": f'openfda.brand_name:"{query}" OR openfda.generic_name:"{query}"',  # Search by brand or generic name
                "limit": 15  # Limit the results to 15 entries
            }

            try:
                # Make a GET request to the FDA API with the search parameters
                response = requests.get(BASE_URL, params=params)
                response.raise_for_status()  # Raise an exception for HTTP errors
                data = response.json()  # Parse the response as JSON
                results = data.get("results", [])  # Extract the "results" array from the response

                medicines = []  # List to store processed medicine data
                for result in results:
                    # Extract relevant medicine information for display
                    medicine_info = {
                        "brand_name": result.get("openfda", {}).get("brand_name", ["N/A"])[0],  # Get brand name or "N/A"
                        "manufacturer": result.get("openfda", {}).get("manufacturer_name", ["N/A"])[0],  # Get manufacturer name or "N/A"
                        "details": {  # Details for the "view details" button
                            "brand_name": result.get("openfda", {}).get("brand_name", ["N/A"])[0],
                            "generic_name": result.get("openfda", {}).get("generic_name", ["N/A"])[0],
                            "manufacturer": result.get("openfda", {}).get("manufacturer_name", ["N/A"])[0],
                            "category": result.get("openfda", {}).get("pharmacologic_class", ["N/A"])[0],
                            "dosage_info": result.get("dosage_and_administration", ["N/A"])[0],  # Dosage information
                            "side_effects": result.get("adverse_reactions", ["N/A"])[0] or result.get("warnings_and_precautions", ["N/A"])[0],  # Side effects or warnings
                            "purpose": result.get("purpose", ["N/A"])[0],  # Purpose of the medicine
                            "indications_and_usage": result.get("indications_and_usage", ["N/A"])[0],  # Indications for usage
                        }
                    }
                    medicines.append(medicine_info)  # Add the processed medicine data to the list

                # Render the template with the form and the medicines data
                return render(request, self.template_name, {'form': form, 'medicines': medicines})
            except requests.exceptions.RequestException as e:
                # Handle errors during the API request (e.g., network issues)
                return render(request, self.template_name, {'form': form, 'error': f"An error occurred: {str(e)}"})
        else:
            # Handle invalid form submission (e.g., empty or invalid query)
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
    
class ScheduleUpdateView(LoginRequiredMixin, UpdateView):
    """
    Allows users to update an existing schedule.
    Ensures that only the owner of the schedule can make modifications.
    """
    model = Schedule  # Specifies the model this view will update
    form_class = ScheduleForm  # Specifies the form class to use for editing
    template_name = 'project/edit_schedule.html'  # Template to render the update form

    def get_object(self, queryset=None):
        """
        Override the method to restrict access.
        Ensures the logged-in user can only update their own schedules.
        """
        schedule = super().get_object(queryset)  # Get the schedule instance
        # Check if the schedule belongs to the current user's profile
        if schedule.user_profile != self.request.user.userprofile:
            # Raise an error if the user is not authorized
            raise HttpResponseForbidden("You are not allowed to edit this schedule.")
        return schedule  # Return the schedule instance for editing

    def get_success_url(self):
        """
        Define the URL to redirect to after a successful update.
        Redirects back to the project home page.
        """
        return reverse('project_home')  # URL name for the home page of the project


class DeleteScheduleView(LoginRequiredMixin, DeleteView):
    """
    Allows users to delete a specific schedule.
    Ensures that only the owner of the schedule can delete it.
    """
    model = Schedule  # Specifies the model this view will delete
    template_name = 'project/delete_med.html'  # Template to confirm the deletion

    def get_object(self, queryset=None):
        """
        Override the method to restrict access.
        Ensures the logged-in user can only delete their own schedules.
        """
        schedule = super().get_object(queryset)  # Get the schedule instance
        # Check if the schedule belongs to the current user's profile
        if schedule.user_profile != self.request.user.userprofile:
            # Raise an error if the user is not authorized
            raise HttpResponseForbidden("You are not allowed to delete this schedule.")
        return schedule  # Return the schedule instance for deletion

    def get_success_url(self):
        """
        Define the URL to redirect to after a successful deletion.
        Redirects to the current week's schedule on the home page.
        """
        return reverse('project_home')  # URL name for the home page of the project

    
class ClearScheduleConfirmView(LoginRequiredMixin, View):
    """
    View to confirm and clear all medicines from the schedule.
    Only affects the logged-in user's schedules.
    """
    def get(self, request, *args, **kwargs):
        # Render the confirmation page
        return render(request, 'project/clear_schedule_confirm.html')

    def post(self, request, *args, **kwargs):
        # Delete all schedules for the logged-in user
        Schedule.objects.filter(user_profile=request.user.userprofile).delete()
        return redirect('project_home')  # Redirect to the home page