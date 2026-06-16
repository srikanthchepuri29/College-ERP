from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.faculty_login, name='faculty_login'),
    path('register/', views.faculty_register, name='faculty_register'),
]
