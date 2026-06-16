import os
import django

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_erp.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta, time
from accounts.models import CustomUser
from academics.models import Department, Course, Subject, Semester, TimetableSlot
from students.models import StudentProfile
from faculty.models import FacultyProfile
from coding_practice.models import CodingProblem, TestCase
from mcq_arena.models import Quiz, Question

def seed_database():
    print("Starting database seeding...")

    # 1. Create Departments
    cse_dept, _ = Department.objects.get_or_create(code="CSE", defaults={"name": "Computer Science & Engineering"})
    ece_dept, _ = Department.objects.get_or_create(code="ECE", defaults={"name": "Electronics & Communication Engineering"})
    print("Departments seeded.")

    # 2. Create Courses
    btech_cse, _ = Course.objects.get_or_create(code="BTECH-CSE", defaults={
        "name": "B.Tech Computer Science",
        "department": cse_dept,
        "duration_years": 4
    })
    btech_ece, _ = Course.objects.get_or_create(code="BTECH-ECE", defaults={
        "name": "B.Tech Electronics",
        "department": ece_dept,
        "duration_years": 4
    })
    print("Courses seeded.")

    # 3. Create active Semester
    semester, _ = Semester.objects.get_or_create(name="Fall 2026", defaults={
        "academic_year": "2026-27",
        "start_date": timezone.now().date() - timedelta(days=30),
        "end_date": timezone.now().date() + timedelta(days=90),
        "is_active": True
    })
    print("Semester seeded.")

    # 4. Create default users and profiles
    # Admin User
    admin_user, created = CustomUser.objects.get_or_create(username="admin", defaults={
        "email": "admin@college.edu",
        "first_name": "System",
        "last_name": "Admin",
        "role": "ADMIN"
    })
    if created:
        admin_user.set_password("adminpassword123")
        admin_user.save()
    print("Admin user seeded.")

    # Faculty User
    faculty_user, created = CustomUser.objects.get_or_create(username="faculty", defaults={
        "email": "faculty@college.edu",
        "first_name": "Alan",
        "last_name": "Turing",
        "role": "FACULTY",
        "is_approved": True # Pre-approved for testing
    })
    if created:
        faculty_user.set_password("facultypassword123")
        faculty_user.save()
        
    faculty_profile, _ = FacultyProfile.objects.get_or_create(user=faculty_user, defaults={
        "faculty_id": "FAC-CSE-001",
        "department": cse_dept,
        "designation": "Professor",
        "phone_number": "+1 (555) 123-4567",
        "qualification": "Ph.D. in Computer Science"
    })
    print("Faculty user and profile seeded.")

    # Student User
    student_user, created = CustomUser.objects.get_or_create(username="student", defaults={
        "email": "student@college.edu",
        "first_name": "Ada",
        "last_name": "Lovelace",
        "role": "STUDENT",
        "is_approved": True # Pre-approved for testing
    })
    if created:
        student_user.set_password("studentpassword123")
        student_user.save()
        
    student_profile, _ = StudentProfile.objects.get_or_create(user=student_user, defaults={
        "student_id": "STU-CSE-2026",
        "department": cse_dept,
        "course": btech_cse,
        "semester": 1,
        "roll_no": "CSE-26-001",
        "phone_number": "+1 (555) 987-6543",
        "admission_year": 2026,
        "address": "123 Computing Way, Silicon Valley, CA"
    })
    print("Student user and profile seeded.")

    # 5. Create Subjects
    py_subject, _ = Subject.objects.get_or_create(code="CSE-101", defaults={
        "name": "Python Programming",
        "course": btech_cse,
        "semester": 1,
        "faculty": faculty_profile,
        "credits": 4
    })
    ds_subject, _ = Subject.objects.get_or_create(code="CSE-102", defaults={
        "name": "Data Structures & Algorithms",
        "course": btech_cse,
        "semester": 1,
        "faculty": faculty_profile,
        "credits": 4
    })
    print("Subjects seeded.")

    # 6. Create Timetable Slots
    TimetableSlot.objects.get_or_create(subject=py_subject, day_of_week=1, defaults={
        "start_time": time(9, 0),
        "end_time": time(10, 30),
        "classroom": "Room 401"
    })
    TimetableSlot.objects.get_or_create(subject=ds_subject, day_of_week=3, defaults={
        "start_time": time(11, 0),
        "end_time": time(12, 30),
        "classroom": "Room 402"
    })
    print("Timetable slots seeded.")

    # 7. Create MCQ Quizzes
    quiz, q_created = Quiz.objects.get_or_create(title="Python Fundamentals Quiz", defaults={
        "description": "A quick assessment covering lists, dictionaries, functions, and control flow in Python.",
        "subject": py_subject,
        "created_by": faculty_profile,
        "duration_minutes": 10,
        "start_time": timezone.now() - timedelta(hours=1),
        "end_time": timezone.now() + timedelta(days=10),
        "is_active": True
    })
    if q_created:
        Question.objects.create(
            quiz=quiz,
            text="Which data structure in Python is mutable and ordered?",
            option_a="Tuple",
            option_b="List",
            option_c="Set",
            option_d="Dictionary",
            correct_option="B",
            marks=2
        )
        Question.objects.create(
            quiz=quiz,
            text="What is the output of len({1, 2, 2, 3})?",
            option_a="4",
            option_b="3",
            option_c="2",
            option_d="5",
            correct_option="B",
            marks=2
        )
        Question.objects.create(
            quiz=quiz,
            text="Which keyword is used to define a function in Python?",
            option_a="func",
            option_b="define",
            option_c="def",
            option_d="function",
            correct_option="C",
            marks=1
        )
    print("MCQ Quiz seeded.")

    # 8. Create Coding Problems & Test Cases
    cp_easy, easy_created = CodingProblem.objects.get_or_create(title="Sum of List Elements", defaults={
        "description": "<p>Write a program that reads a list of numbers from standard input and prints their sum.</p><p>Input elements are separated by space.</p>",
        "difficulty": "Easy",
        "input_format": "A single line containing integers separated by space.",
        "output_format": "A single integer denoting the sum.",
        "sample_input": "1 2 3 4 5",
        "sample_output": "15",
        "time_limit_seconds": 2,
        "memory_limit_mb": 256,
        "created_by": admin_user
    })
    if easy_created:
        TestCase.objects.create(problem=cp_easy, input_data="1 2 3 4 5", expected_output="15", is_sample=True)
        TestCase.objects.create(problem=cp_easy, input_data="10 -2 5", expected_output="13", is_sample=False)
        TestCase.objects.create(problem=cp_easy, input_data="0 0 0", expected_output="0", is_sample=False)

    cp_med, med_created = CodingProblem.objects.get_or_create(title="Find Prime Numbers", defaults={
        "description": "<p>Write a program that takes an integer N from input and outputs 'PRIME' if N is prime, or 'NOT' if it is not prime.</p>",
        "difficulty": "Medium",
        "input_format": "An integer N.",
        "output_format": "PRIME or NOT.",
        "sample_input": "7",
        "sample_output": "PRIME",
        "time_limit_seconds": 2,
        "memory_limit_mb": 256,
        "created_by": admin_user
    })
    if med_created:
        TestCase.objects.create(problem=cp_med, input_data="7", expected_output="PRIME", is_sample=True)
        TestCase.objects.create(problem=cp_med, input_data="4", expected_output="NOT", is_sample=False)
        TestCase.objects.create(problem=cp_med, input_data="11", expected_output="PRIME", is_sample=False)
        TestCase.objects.create(problem=cp_med, input_data="1", expected_output="NOT", is_sample=False)

    print("Coding challenges seeded.")
    print("Database seeding completed successfully!")
    print("\n--- DEMO USER CREDENTIALS ---")
    print("Admin:   username: admin    password: adminpassword123")
    print("Faculty: username: faculty  password: facultypassword123")
    print("Student: username: student  password: studentpassword123")
    print("-----------------------------\n")

if __name__ == "__main__":
    seed_database()
