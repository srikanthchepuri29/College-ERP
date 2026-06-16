from rest_framework import serializers
from coding_practice.models import CodingProblem, CodingSubmission

class CodingProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodingProblem
        fields = ['id', 'title', 'description', 'difficulty', 'input_format', 'output_format', 'sample_input', 'sample_output', 'time_limit_seconds', 'memory_limit_mb']

class CodingSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    problem_title = serializers.CharField(source='problem.title', read_only=True)

    class Meta:
        model = CodingSubmission
        fields = ['id', 'problem', 'problem_title', 'student', 'student_name', 'code', 'language', 'status', 'runtime_ms', 'submitted_at']

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"
