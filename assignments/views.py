from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from accounts.permissions import IsAdminUserRole, IsFacultyUserRole, IsStudentUserRole
from assignments.models import Assignment, AssignmentSubmission
from assignments.serializers import AssignmentSerializer, AssignmentSubmissionSerializer

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all().order_by('-deadline')
    serializer_class = AssignmentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsFacultyUserRole() | IsAdminUserRole()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'faculty_profile'):
            serializer.save(created_by=self.request.user.faculty_profile)
        else:
            serializer.save()

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Assignment.objects.all()
        elif user.role == 'FACULTY' and hasattr(user, 'faculty_profile'):
            return Assignment.objects.filter(created_by=user.faculty_profile)
        elif user.role == 'STUDENT' and hasattr(user, 'student_profile'):
            # Show assignments matching student's course and semester
            profile = user.student_profile
            return Assignment.objects.filter(subject__course=profile.course, subject__semester=profile.semester)
        return Assignment.objects.none()

class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    queryset = AssignmentSubmission.objects.all()
    serializer_class = AssignmentSubmissionSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [IsStudentUserRole()]
        elif self.action in ['update', 'partial_update']:
            return [IsFacultyUserRole() | IsAdminUserRole()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user.student_profile)

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return AssignmentSubmission.objects.all()
        elif user.role == 'FACULTY' and hasattr(user, 'faculty_profile'):
            # Faculty sees submissions for their assignments
            return AssignmentSubmission.objects.filter(assignment__created_by=user.faculty_profile)
        elif user.role == 'STUDENT' and hasattr(user, 'student_profile'):
            # Students see their own submissions
            return AssignmentSubmission.objects.filter(student=user.student_profile)
        return AssignmentSubmission.objects.none()
