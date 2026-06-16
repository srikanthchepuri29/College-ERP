from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('reject/<int:user_id>/', views.reject_user, name='reject_user'),
    path('schedule/', views.admin_schedule, name='admin_schedule'),
    path('schedule/add/', views.add_schedule_slot, name='add_schedule_slot'),
    path('schedule/delete/<int:slot_id>/', views.delete_schedule_slot, name='delete_schedule_slot'),
    path('attendance/', views.admin_attendance, name='admin_attendance'),
    path('attendance/save/', views.save_attendance, name='save_attendance'),
    path('marks/', views.admin_marks, name='admin_marks'),
    path('marks/add-exam/', views.add_exam, name='admin_add_exam'),
    path('marks/save/', views.save_marks, name='admin_save_marks'),
]
