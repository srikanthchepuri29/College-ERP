from django.urls import path, include

urlpatterns = [
    path('admin/', include('dashboard.admin_dashboard.urls')),
    path('faculty/', include('dashboard.faculty_dashboard.urls')),
    path('student/', include('dashboard.student_dashboard.urls')),
]
