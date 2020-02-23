# pizza/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('', views.room, name='room'),
    path('chat/', views.room, name='room')
]
