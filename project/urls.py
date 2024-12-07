from django.urls import path
from .views import MedicineListView, ScheduleCreateView, InteractionCheckView, ScheduleView, MedicineSearchView
from .views import MedicineDetailView

urlpatterns = [
    path(r'', ScheduleView.as_view(), name='project_home'),
    path(r'medicines/', MedicineListView.as_view(), name='list_medicines'),
    path(r'add_schedule/', ScheduleCreateView.as_view(), name='add_schedule'),
    path(r'check_interactions/', InteractionCheckView.as_view(), name='check_interactions'),
    path(r'medicine_search/', MedicineSearchView.as_view(), name='medicine_search'),
    path(r'medicine_detail/', MedicineDetailView.as_view(), name='medicine_detail'),
]