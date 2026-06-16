from django.urls import path, include
from accounts.admin_auth import views as admin_views

urlpatterns = [
    path('admin/', include('accounts.admin_auth.urls')),
    path('faculty/', include('accounts.faculty_auth.urls')),
    path('student/', include('accounts.student_auth.urls')),
    path('logout/', admin_views.user_logout, name='logout'),
]
