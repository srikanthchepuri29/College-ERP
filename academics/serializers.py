from rest_framework import serializers
from academics.models import Department, Course, Subject, Semester, TimetableSlot, FeeRecord

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'department', 'department_name', 'duration_years']

class SubjectSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    faculty_name = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'course', 'course_name', 'semester', 'faculty', 'faculty_name', 'credits']

    def get_faculty_name(self, obj):
        if obj.faculty:
            return f"{obj.faculty.user.first_name} {obj.faculty.user.last_name}"
        return "Not Assigned"

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = '__all__'

class TimetableSlotSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = TimetableSlot
        fields = ['id', 'subject', 'subject_name', 'subject_code', 'day_of_week', 'day_name', 'start_time', 'end_time', 'classroom']

class FeeRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    semester_name = serializers.CharField(source='semester.name', read_only=True)

    class Meta:
        model = FeeRecord
        fields = ['id', 'student', 'student_name', 'semester', 'semester_name', 'amount', 'due_date', 'status', 'payment_date', 'transaction_id']

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"
