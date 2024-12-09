from django.urls import path
from .views import MedicineListView, ScheduleCreateView, InteractionCheckView, ScheduleView, MedicineSearchView
from .views import MedicineDetailView, MedicineDetailFromListView, MedicineDeleteView, ScheduleUpdateView
from .views import DeleteScheduleView, ClearScheduleConfirmView
from . import views

urlpatterns = [
    path(r'', ScheduleView.as_view(), name='project_home'),
    path(r'medicines/', MedicineListView.as_view(), name='medicines'),
    path(r'add_to_schedule/', ScheduleCreateView.as_view(), name='add_schedule'),
    path(r'check_interactions/', InteractionCheckView.as_view(), name='check_interactions'),
    path(r'medicine_search/', MedicineSearchView.as_view(), name='medicine_search'),
    path(r'medicine_detail/', MedicineDetailView.as_view(), name='medicine_detail'),
    path(r'medicine_detail_from_list/', MedicineDetailFromListView.as_view(), name='medicine_detail_from_list'),
    path(r'add_to_medicines/', views.add_to_medicines, name='add_to_medicines'),
    path(r'delete_medicine/<int:pk>/', MedicineDeleteView.as_view(), name='delete_medicine'),
    path(r'edit_schedule/<int:pk>/', ScheduleUpdateView.as_view(), name='edit_schedule'),
    path(r'delete_med/<int:pk>/', DeleteScheduleView.as_view(), name='delete_med'),
    path(r'clear_schedule/', ClearScheduleConfirmView.as_view(), name='clear_schedule'),
]