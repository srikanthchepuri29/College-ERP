from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdminUserRole
from faculty.models import FacultyProfile
from faculty.serializers import FacultyProfileSerializer

class FacultyProfileViewSet(viewsets.ModelViewSet):
    queryset = FacultyProfile.objects.all()
    serializer_class = FacultyProfileSerializer

    def get_permissions(self):
        if self.action in ['destroy']:
            return [IsAdminUserRole()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN' or user.role == 'STUDENT':
            return FacultyProfile.objects.all()
        elif user.role == 'FACULTY' and hasattr(user, 'faculty_profile'):
            return FacultyProfile.objects.filter(id=user.faculty_profile.id)
        return FacultyProfile.objects.none()
