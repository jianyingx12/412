from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.quotes, name='main_page'),
    path(r'show_all', views.show_all, name='show_all'), 
    path(r'about', views.about, name='about'), 
]