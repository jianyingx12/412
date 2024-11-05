from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .models import Profile, StatusMessage, Image
from .forms import CreateProfileForm, CreateStatusMessageForm, UpdateProfileForm
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from typing import Any
from django.contrib.auth import login

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
    form_class = CreateProfileForm  
    template_name = 'mini_fb/create_profile_form.html'  

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
        context = super().get_context_data(**kwargs)
        # Pass an instance of UserCreationForm to the template context
        context['user_form'] = kwargs.get('user_form', UserCreationForm())
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
        '''Redirect to show all profiles after successful profile creation.'''
        return reverse('show_all_profiles')

    
class CreateStatusMessageView(LoginRequiredMixin, CreateView):
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
        '''Provide the profile context to the template.'''
        context = super().get_context_data(**kwargs)
        # Retrieve the profile for the logged-in user
        profile = Profile.objects.get(user=self.request.user)
        context['profile'] = profile
        return context

    def form_valid(self, form):
        '''Attach the profile and handle uploaded images.'''
        # Retrieve the profile for the logged-in user
        profile = Profile.objects.get(user=self.request.user)

        # attach this profile to the instance of the Comment 
        form.instance.profile = profile

        # Save the status message
        sm = form.save()  

        # Handle the uploaded images
        files = self.request.FILES.getlist('files')
        for file in files:
            # Create an Image object for each uploaded file
            image = Image(status_message=sm, image_file=file)
            image.save()  # Save the Image object to the database

        # delegate work to superclass version of this method
        return super().form_valid(form)

    def get_success_url(self):
        '''Redirect to the profile page after successful status creation.'''
        # Redirect to the logged-in user's profile page
        profile = Profile.objects.get(user=self.request.user)
        return reverse('show_profile', kwargs={'pk': profile.pk})
    
class UpdateProfileView(LoginRequiredMixin, UpdateView):
    '''Update a profile'''
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'

    def get_success_url(self):
        # Redirect to the profile page after updating
        return reverse('show_profile', kwargs={'pk': self.object.pk})
    
    # Get profile for current user
    def get_object(self):
        return Profile.objects.get(user=self.request.user)

class DeleteStatusMessageView(LoginRequiredMixin, DeleteView):
    '''Delete status message'''
    model = StatusMessage 
    template_name = 'mini_fb/delete_status_form.html'
    context_object_name = 'status_message'

    def get_success_url(self):
        # Redirect to the profile page after deletion
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})
    
class UpdateStatusMessageView(LoginRequiredMixin, UpdateView):
    '''Update status message'''
    model = StatusMessage
    fields = ['message'] 
    template_name = 'mini_fb/update_status_form.html'
    context_object_name = 'status_message'

    def get_success_url(self):
        # Redirect to the profile page after updating
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})
    
class CreateFriendView(LoginRequiredMixin, View):
    '''Create a Friend'''
    def dispatch(self, *_, **kwargs):
        profile = get_object_or_404(Profile, pk=kwargs['pk'])
        other_profile = get_object_or_404(Profile, pk=kwargs['other_pk'])
        profile.add_friend(other_profile)
        return redirect('show_profile', pk=profile.pk)
    
class ShowFriendSuggestionsView(LoginRequiredMixin, DetailView):
    '''Show Friend Suggestions'''
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'
    context_object_name = 'profile'

    # Get profile for current user
    def get_object(self):
        return Profile.objects.get(user=self.request.user)

class ShowNewsFeedView(LoginRequiredMixin, DetailView):
    '''Show newsfeed'''
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'

    # Get profile for current user
    def get_object(self):
        return Profile.objects.get(user=self.request.user)