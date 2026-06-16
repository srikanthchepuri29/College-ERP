from django.shortcuts import render
from students.models import StudentProfile
from faculty.models import FacultyProfile
from academics.models import Department

def home_page(request):
    # Statistics to display on the Landing Page Hero/Stats section
    total_students = StudentProfile.objects.count()
    total_faculty = FacultyProfile.objects.count()
    total_depts = Department.objects.count()
    
    context = {
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_depts': total_depts,
    }
    return render(request, 'home.html', context)
