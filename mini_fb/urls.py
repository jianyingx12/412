from django.urls import path
from django.conf import settings
from . import views
from .views import ShowAllProfilesView

# all of the URLs that are part of this app
urlpatterns = [
    path(r'', ShowAllProfilesView.as_view(), name='show_all_profiles'),
]