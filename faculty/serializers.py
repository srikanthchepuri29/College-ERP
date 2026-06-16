from rest_framework import serializers
from faculty.models import FacultyProfile
from accounts.serializers import CustomUserSerializer

class FacultyProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = FacultyProfile
        fields = ['id', 'user', 'faculty_id', 'department', 'department_name', 'designation', 'phone_number', 'qualification', 'office_hours']
