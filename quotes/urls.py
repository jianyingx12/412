from django.urls import path
from . import views

urlpatterns = [
    path(r'', views.quotes, name='main_page'),
    path(r'show_all', views.show_all, name='show_all'), 
    path(r'about', views.about, name='about'), 
]