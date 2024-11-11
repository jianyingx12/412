from django.urls import path
from .views import VoterListView, VoterDetailView, GraphsView

urlpatterns = [
    path(r'', VoterListView.as_view(), name='voters'),
    path(r'voter/<int:pk>/', VoterDetailView.as_view(), name='voter'),
    path(r'graphs/', GraphsView.as_view(), name='graphs'),
]