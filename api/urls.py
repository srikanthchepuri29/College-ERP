from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Import ViewSets from individual apps
from accounts.views import UserViewSet
from academics.views import (
    DepartmentViewSet, CourseViewSet, SubjectViewSet,
    SemesterViewSet, TimetableSlotViewSet, FeeRecordViewSet
)
from students.views import StudentProfileViewSet
from faculty.views import FacultyProfileViewSet
from lms.views import LMSMaterialViewSet
from assignments.views import AssignmentViewSet, AssignmentSubmissionViewSet
from mcq_arena.views import QuizViewSet, QuestionViewSet, QuizAttemptViewSet
from coding_practice.views import CodingProblemViewSet, CodingSubmissionViewSet
from attendance.views import AttendanceRecordViewSet
from results.views import ExamScheduleViewSet, ResultViewSet
from notifications.views import NotificationViewSet

router = DefaultRouter()

# Register routes with the router
router.register(r'users', UserViewSet, basename='user')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'semesters', SemesterViewSet, basename='semester')
router.register(r'timetable', TimetableSlotViewSet, basename='timetable')
router.register(r'fees', FeeRecordViewSet, basename='fee')
router.register(r'students', StudentProfileViewSet, basename='student-profile')
router.register(r'faculty', FacultyProfileViewSet, basename='faculty-profile')
router.register(r'lms', LMSMaterialViewSet, basename='lms-material')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'submissions', AssignmentSubmissionViewSet, basename='assignment-submission')
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'quiz-attempts', QuizAttemptViewSet, basename='quiz-attempt')
router.register(r'coding-problems', CodingProblemViewSet, basename='coding-problem')
router.register(r'coding-submissions', CodingSubmissionViewSet, basename='coding-submission')
router.register(r'attendance', AttendanceRecordViewSet, basename='attendance')
router.register(r'exams', ExamScheduleViewSet, basename='exam')
router.register(r'results', ResultViewSet, basename='result')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    # Include all auto-generated ViewSet routes
    path('', include(router.urls)),
    
    # JWT Auth endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
