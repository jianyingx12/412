from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .models import Profile, StatusMessage, Image
from .forms import CreateProfileForm, CreateStatusMessageForm, UpdateProfileForm
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin

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

class CreateProfileView(LoginRequiredMixin, CreateView):
    '''Create a profile'''
    model = Profile
    form_class = CreateProfileForm
    template_name = 'mini_fb/create_profile_form.html'

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.pk})
    
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
        # find the profile identified by the PK from the URL pattern
        # add the profile referred to by the URL into this context
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        
        # find the profile identified by the PK from the URL pattern
        profile = Profile.objects.get(pk=self.kwargs['pk'])

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
        # find the profile identified by the PK from the URL pattern
        return reverse('show_profile', kwargs={'pk': self.kwargs['pk']})
    
class UpdateProfileView(LoginRequiredMixin, UpdateView):
    '''Update a profile'''
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'

    def get_queryset(self):
    # get objects related to the currently logged-in user
        return Profile.objects.filter(user=self.request.user)

    def get_success_url(self):
        # Redirect to the profile page after updating
        return reverse('show_profile', kwargs={'pk': self.object.pk})

class DeleteStatusMessageView(LoginRequiredMixin, DeleteView):
    '''Delete status message'''
    model = StatusMessage 
    template_name = 'mini_fb/delete_status_form.html'
    context_object_name = 'status_message'

    def get_success_url(self):
        # Redirect to the profile page after deletion
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})
    
    def get_queryset(self):
        # Limit deletion to the user's own status messages
        return StatusMessage.objects.filter(profile__user=self.request.user)
    
class UpdateStatusMessageView(LoginRequiredMixin, UpdateView):
    '''Update status message'''
    model = StatusMessage
    fields = ['message'] 
    template_name = 'mini_fb/update_status_form.html'
    context_object_name = 'status_message'

    def get_success_url(self):
        # Redirect to the profile page after updating
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})
    
    def get_queryset(self):
        # Limit updates to the user's own status messages
        return StatusMessage.objects.filter(profile__user=self.request.user)
    
class CreateFriendView(View):
    '''Create a Friend'''
    def dispatch(self, *_, **kwargs):
        profile = get_object_or_404(Profile, pk=kwargs['pk'])
        other_profile = get_object_or_404(Profile, pk=kwargs['other_pk'])
        profile.add_friend(other_profile)
        return redirect('show_profile', pk=profile.pk)
    
class ShowFriendSuggestionsView(DetailView):
    '''Show Friend Suggestions'''
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'
    context_object_name = 'profile'

class ShowNewsFeedView(DetailView):
    '''Show newsfeed'''
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'