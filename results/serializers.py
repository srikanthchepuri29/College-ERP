from rest_framework import serializers
from results.models import ExamSchedule, Result

class ExamScheduleSerializer(serializers.ModelSerializer):
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = ExamSchedule
        fields = ['id', 'name', 'subject', 'subject_code', 'subject_name', 'exam_type', 'date', 'max_marks']

class ResultSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_id_str = serializers.CharField(source='student.student_id', read_only=True)
    exam_name = serializers.CharField(source='exam_schedule.name', read_only=True)
    subject_code = serializers.CharField(source='exam_schedule.subject.code', read_only=True)
    max_marks = serializers.IntegerField(source='exam_schedule.max_marks', read_only=True)

    class Meta:
        model = Result
        fields = ['id', 'exam_schedule', 'exam_name', 'subject_code', 'student', 'student_name', 'student_id_str', 'marks_obtained', 'max_marks', 'grade', 'remarks']

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"
