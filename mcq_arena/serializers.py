from rest_framework import serializers
from mcq_arena.models import Quiz, Question, QuizAttempt

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'marks']
        # Hide correct answer from students during serialized responses if needed, but for standard editing/attempts we include it.
        # We will strip correct answers on the attempt list view for students.

class QuizSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'subject', 'subject_name', 'created_by', 'created_by_name', 'duration_minutes', 'start_time', 'end_time', 'is_active', 'questions']

    def get_created_by_name(self, obj):
        return f"{obj.created_by.user.first_name} {obj.created_by.user.last_name}"

class QuizAttemptSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'quiz_title', 'student', 'student_name', 'score', 'answers_json', 'submitted_at']

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"
