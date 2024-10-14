from django.urls import path
from django.conf import settings
from . import views
from .views import ShowAllProfilesView
from .views import ShowProfilePageView
from .views import CreateProfileView
from .views import CreateStatusMessageView

# all of the URLs that are part of this app
urlpatterns = [
    path(r'', ShowAllProfilesView.as_view(), name='show_all_profiles'),
    path(r'profile/<int:pk>/', ShowProfilePageView.as_view(), name='show_profile'),
    path(r'create_profile/', CreateProfileView.as_view(), name='create_profile'),
    path(r'profile/<int:pk>/create_status/', CreateStatusMessageView.as_view(), name='create_status'),
]