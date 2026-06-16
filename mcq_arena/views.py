from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from mcq_arena.models import Quiz, Question, QuizAttempt
from mcq_arena.serializers import QuizSerializer, QuestionSerializer, QuizAttemptSerializer
from accounts.permissions import IsAdminUserRole, IsFacultyUserRole, IsStudentUserRole

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all().order_by('-start_time')
    serializer_class = QuizSerializer

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
            return Quiz.objects.all()
        elif user.role == 'FACULTY' and hasattr(user, 'faculty_profile'):
            return Quiz.objects.filter(created_by=user.faculty_profile)
        elif user.role == 'STUDENT' and hasattr(user, 'student_profile'):
            profile = user.student_profile
            return Quiz.objects.filter(subject__course=profile.course, subject__semester=profile.semester, is_active=True)
        return Quiz.objects.none()

    @action(detail=True, methods=['post'], permission_classes=[IsStudentUserRole])
    def submit_quiz(self, request, pk=None):
        quiz = self.get_object()
        student = request.user.student_profile
        answers = request.data.get('answers', {}) # e.g. {"1": "A", "2": "C"}
        
        if QuizAttempt.objects.filter(quiz=quiz, student=student).exists():
            return Response({'error': 'You have already attempted this quiz.'}, status=status.HTTP_400_BAD_REQUEST)
            
        total_score = 0
        questions = quiz.questions.all()
        total_possible = sum(q.marks for q in questions)
        
        for question in questions:
            submitted_option = answers.get(str(question.id))
            if submitted_option and submitted_option.strip().upper() == question.correct_option.strip().upper():
                total_score += question.marks
                
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            student=student,
            score=total_score,
            answers_json=answers
        )
        
        return Response({
            'status': 'success',
            'score': total_score,
            'total_possible': total_possible,
            'attempt_id': attempt.id
        })

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsFacultyUserRole() | IsAdminUserRole()]
        return [IsAuthenticated()]

class QuizAttemptViewSet(viewsets.ModelViewSet):
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return QuizAttempt.objects.all()
        elif user.role == 'FACULTY' and hasattr(user, 'faculty_profile'):
            return QuizAttempt.objects.filter(quiz__created_by=user.faculty_profile)
        elif user.role == 'STUDENT' and hasattr(user, 'student_profile'):
            return QuizAttempt.objects.filter(student=user.student_profile)
        return QuizAttempt.objects.none()
