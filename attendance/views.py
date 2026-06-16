from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdminUserRole, IsFacultyUserRole
from attendance.models import AttendanceRecord
from attendance.serializers import AttendanceRecordSerializer

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.all().order_by('-date')
    serializer_class = AttendanceRecordSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsFacultyUserRole() | IsAdminUserRole()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'faculty_profile'):
            serializer.save(marked_by=self.request.user.faculty_profile)
        else:
            serializer.save()

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN' or user.role == 'FACULTY':
            return AttendanceRecord.objects.all()
        elif user.role == 'STUDENT' and hasattr(user, 'student_profile'):
            return AttendanceRecord.objects.filter(student=user.student_profile)
        return AttendanceRecord.objects.none()
