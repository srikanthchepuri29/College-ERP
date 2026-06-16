from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdminUserRole
from students.models import StudentProfile
from students.serializers import StudentProfileSerializer

class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer

    def get_permissions(self):
        if self.action in ['destroy']:
            return [IsAdminUserRole()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN' or user.role == 'FACULTY':
            return StudentProfile.objects.all()
        elif user.role == 'STUDENT' and hasattr(user, 'student_profile'):
            return StudentProfile.objects.filter(id=user.student_profile.id)
        return StudentProfile.objects.none()
