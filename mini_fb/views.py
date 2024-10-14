from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from .models import Profile, StatusMessage
from .forms import CreateProfileForm, CreateStatusMessageForm
from django.urls import reverse

# Create your views here.

class ShowAllProfilesView(ListView):
    '''the view to show all profiles'''
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'

class ShowProfilePageView(DetailView):
    '''Display one profile selected'''
    model = Profile
    template_name = 'mini_fb/show_profile.html'
    context_object_name = 'profile'

class CreateProfileView(CreateView):
    '''Create a profile'''
    model = Profile
    form_class = CreateProfileForm
    template_name = 'mini_fb/create_profile_form.html'

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.pk})
    
class CreateStatusMessageView(CreateView):
    '''
    A view to create a status message on a profile.
    on GET: send back the form to display
    on POST: read/process the form, and save new Comment to the database
    '''
    model = StatusMessage
    form_class = CreateStatusMessageForm
    template_name = 'mini_fb/create_status_form.html'

    # get the context data from the sueprclass
    def get_context_data(self, **kwargs):
        # find the profile identified by the PK from the URL pattern
        # add the profile referred to by the URL into this context
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        
        # find the profile identified by the PK from the URL pattern
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        # attach this profile to the instance of the Comment to set its FK
        form.instance.profile = profile
        # delegate work to superclass version of this method
        return super().form_valid(form)

    def get_success_url(self):
        # find the profile identified by the PK from the URL pattern
        return reverse('show_profile', kwargs={'pk': self.kwargs['pk']})