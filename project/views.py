from django.views.generic import ListView, CreateView, TemplateView
from django.shortcuts import redirect
from .models import Medicine, Schedule, Interaction
from .forms import ScheduleForm  

# Medicine List View
class MedicineListView(ListView):
    """
    Displays all medicines stored in the database.
    """
    model = Medicine
    template_name = 'medicines.html'  # Template for the medicine list
    context_object_name = 'medicines'  # Variable to use in the template


# Add Medicine to Schedule View
class ScheduleCreateView(CreateView):
    """
    Allows users to add a medicine to the schedule using a form.
    """
    model = Schedule
    form_class = ScheduleForm
    template_name = 'add_schedule.html'  # Template for the form
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
    template_name = 'interactions.html'

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
    """
    Displays a weekly schedule of medicines.
    """
    template_name = 'project/schedule.html'

    def get_context_data(self, **kwargs):
        """
        Add the user's weekly schedule to the context.
        """
        context = super().get_context_data(**kwargs)

        # Query schedules for now
        schedules = Schedule.objects.all().order_by('time')

        # Organize schedules by day of the week
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_schedule = {day: [] for day in days_of_week}
        non_day_schedules = []  # Group schedules that don't match a day

        for schedule in schedules:
            if schedule.frequency in weekly_schedule:
                weekly_schedule[schedule.frequency].append(schedule)
            else:
                non_day_schedules.append(schedule)  # Add non-day schedules separately

        context['weekly_schedule'] = weekly_schedule
        context['non_day_schedules'] = non_day_schedules  # Pass non-day schedules to the template
        return context

