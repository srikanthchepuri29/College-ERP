from django.urls import path
from . import views

urlpatterns = [
    path('', views.faculty_dashboard, name='faculty_dashboard'),
    path('grade/<int:submission_id>/', views.grade_submission, name='grade_submission'),
    path('assignment/add/', views.add_assignment, name='add_assignment'),
    path('quiz/add/', views.add_quiz, name='add_quiz'),
    path('quiz/<int:quiz_id>/add-question/', views.add_question, name='add_question'),
    path('schedule/', views.faculty_schedule, name='faculty_schedule'),
    path('marks/', views.faculty_marks, name='faculty_marks'),
    path('marks/add-exam/', views.add_exam, name='faculty_add_exam'),
    path('marks/save/', views.save_marks, name='faculty_save_marks'),
    path('attendance/', views.faculty_attendance, name='faculty_attendance'),
]
