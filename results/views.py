from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdminUserRole, IsFacultyUserRole
from results.models import ExamSchedule, Result
from results.serializers import ExamScheduleSerializer, ResultSerializer

class ExamScheduleViewSet(viewsets.ModelViewSet):
    queryset = ExamSchedule.objects.all().order_by('-date')
    serializer_class = ExamScheduleSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsFacultyUserRole() | IsAdminUserRole()]
        return [IsAuthenticated()]

class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsFacultyUserRole() | IsAdminUserRole()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN' or user.role == 'FACULTY':
            return Result.objects.all()
        elif user.role == 'STUDENT' and hasattr(user, 'student_profile'):
            return Result.objects.filter(student=user.student_profile)
        return Result.objects.none()
