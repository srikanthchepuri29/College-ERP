from rest_framework import serializers
from assignments.models import Assignment, AssignmentSubmission

class AssignmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'subject', 'subject_name', 'created_by', 'created_by_name', 'deadline', 'max_marks', 'file']

    def get_created_by_name(self, obj):
        return f"{obj.created_by.user.first_name} {obj.created_by.user.last_name}"

class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_id_str = serializers.CharField(source='student.student_id', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'assignment', 'assignment_title', 'student', 'student_name', 'student_id_str', 'file', 'submitted_at', 'marks_obtained', 'feedback', 'is_evaluated']

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"
