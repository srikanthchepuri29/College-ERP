from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_dashboard, name='student_dashboard'),
    path('submit/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    path('schedule/', views.student_schedule, name='student_schedule'),
    path('marks/', views.student_marks, name='student_marks'),
    path('exams/', views.student_exams, name='student_exams'),
    path('exams/submit/<int:exam_id>/', views.submit_exam, name='submit_exam'),
    path('attendance/', views.student_attendance, name='student_attendance'),
]
