from rest_framework import serializers
from students.models import StudentProfile
from accounts.serializers import CustomUserSerializer

class StudentProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'student_id', 'department', 'department_name', 'course', 'course_name', 'semester', 'roll_no', 'date_of_birth', 'phone_number', 'admission_year', 'address']
