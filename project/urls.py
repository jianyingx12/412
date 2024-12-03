from django.urls import path
from .views import MedicineListView, ScheduleCreateView, InteractionCheckView, ScheduleView

urlpatterns = [
    path(r'', ScheduleView.as_view(), name='project_home'),
    path(r'medicines/', MedicineListView.as_view(), name='list_medicines'),
    path(r'add_schedule/', ScheduleCreateView.as_view(), name='add_schedule'),
    path(r'check_interactions/', InteractionCheckView.as_view(), name='check_interactions'),
]