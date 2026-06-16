
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date
from accounts.models import CustomUser
from students.models import StudentProfile
from faculty.models import FacultyProfile
from academics.models import Department, Course, Subject
from results.models import ExamSchedule, Result, ExamSubmission
from attendance.models import AttendanceRecord

class ExamPortalTests(TestCase):
    def setUp(self):
        # 1. Create department
        self.dept = Department.objects.create(name="Computer Science", code="CS")
        
        # 2. Create course
        self.course = Course.objects.create(name="B.Tech Computer Science", code="CS-BTECH", department=self.dept)
        
        # 3. Create users
        # Admin
        self.admin_user = CustomUser.objects.create_user(
            username="admin1", email="admin1@college.edu", password="password123", role="ADMIN", is_approved=True
        )
        
        # Faculty
        self.faculty_user = CustomUser.objects.create_user(
            username="faculty1", email="faculty1@college.edu", password="password123", role="FACULTY", is_approved=True
        )
        self.faculty_profile = FacultyProfile.objects.create(
            user=self.faculty_user, faculty_id="FAC001", department=self.dept
        )
        
        # Student
        self.student_user = CustomUser.objects.create_user(
            username="student1", email="student1@college.edu", password="password123", role="STUDENT", is_approved=True
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user, student_id="STU001", department=self.dept, course=self.course, semester=1
        )
        
        # 4. Create subject
        self.subject = Subject.objects.create(
            name="Data Structures", code="CS101", course=self.course, semester=1, faculty=self.faculty_profile
        )
        
        # 5. Create exam schedule
        self.exam = ExamSchedule.objects.create(
            name="Midterm Exam 1", subject=self.subject, exam_type="INTERNAL", date=date.today(), max_marks=100
        )
        
    def test_student_views_exams(self):
        # Login student
        self.client.login(username="student1", password="password123")
        response = self.client.get(reverse('student_exams'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Midterm Exam 1")
        
    def test_student_submits_exam(self):
        self.client.login(username="student1", password="password123")
        submit_url = reverse('submit_exam', args=[self.exam.id])
        
        # Post answer
        response = self.client.post(submit_url, {
            'answers': "This is my exam response."
        })
        self.assertRedirects(response, reverse('student_exams'))
        
        # Check database
        submission = ExamSubmission.objects.get(exam_schedule=self.exam, student=self.student_profile)
        self.assertEqual(submission.answers, "This is my exam response.")
        
    def test_faculty_view_submission(self):
        # Create submission
        ExamSubmission.objects.create(
            exam_schedule=self.exam, student=self.student_profile, answers="Student answers."
        )
        
        # Login faculty
        self.client.login(username="faculty1", password="password123")
        response = self.client.get(f"{reverse('faculty_marks')}?exam={self.exam.id}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Student answers.")
        
    def test_admin_view_submission(self):
        # Create submission
        ExamSubmission.objects.create(
            exam_schedule=self.exam, student=self.student_profile, answers="Student answers."
        )
        
        # Login admin
        self.client.login(username="admin1", password="password123")
        response = self.client.get(f"{reverse('admin_marks')}?exam={self.exam.id}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Student answers.")


class AttendancePortalTests(TestCase):
    def setUp(self):
        # Create department
        self.dept = Department.objects.create(name="Computer Science", code="CS")
        
        # Create course
        self.course = Course.objects.create(name="B.Tech Computer Science", code="CS-BTECH", department=self.dept)
        
        # Admin
        self.admin_user = CustomUser.objects.create_user(
            username="admin1", email="admin1@college.edu", password="password123", role="ADMIN", is_approved=True
        )
        
        # Faculty
        self.faculty_user = CustomUser.objects.create_user(
            username="faculty1", email="faculty1@college.edu", password="password123", role="FACULTY", is_approved=True
        )
        self.faculty_profile = FacultyProfile.objects.create(
            user=self.faculty_user, faculty_id="FAC001", department=self.dept
        )
        
        # Student
        self.student_user = CustomUser.objects.create_user(
            username="student1", email="student1@college.edu", password="password123", role="STUDENT", is_approved=True
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user, student_id="STU001", department=self.dept, course=self.course, semester=1
        )
        
        # Subject
        self.subject = Subject.objects.create(
            name="Data Structures", code="CS101", course=self.course, semester=1, faculty=self.faculty_profile
        )

    def test_student_views_attendance(self):
        self.client.login(username="student1", password="password123")
        # Access student attendance page
        response = self.client.get(reverse('student_attendance'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Data Structures")
        
        # Should NOT allow student to save attendance
        response = self.client.post(reverse('save_attendance'), {
            'student_id': self.student_profile.id,
            'subject_id': self.subject.id,
            'date': '2026-06-15',
            'status': 'PRESENT'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_faculty_manages_attendance(self):
        self.client.login(username="faculty1", password="password123")
        # Access faculty attendance page
        response = self.client.get(reverse('faculty_attendance'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Data Structures")
        
        # Should allow faculty to save attendance
        response = self.client.post(reverse('save_attendance'), {
            'student_id': self.student_profile.id,
            'subject_id': self.subject.id,
            'date': '2026-06-15',
            'status': 'PRESENT'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Check database
        record = AttendanceRecord.objects.get(student=self.student_profile, subject=self.subject, date='2026-06-15')
        self.assertEqual(record.status, 'PRESENT')


class AdminCreationTests(TestCase):
    def setUp(self):
        # Admin User
        self.admin_user = CustomUser.objects.create_user(
            username="admin1", email="admin1@college.edu", password="password123", role="ADMIN", is_approved=True
        )
        # Non-Admin User (Faculty)
        self.faculty_user = CustomUser.objects.create_user(
            username="faculty1", email="faculty1@college.edu", password="password123", role="FACULTY", is_approved=True
        )
        # Create a Department for reference
        self.dept = Department.objects.create(name="Electronics", code="ECE")
        
        # Create a Course for reference
        self.course = Course.objects.create(name="B.Tech ECE", code="ECE-BTECH", department=self.dept)

    def test_admin_add_department(self):
        self.client.login(username="admin1", password="password123")
        response = self.client.post(reverse('admin_add_department'), {
            'name': 'Civil Engineering',
            'code': 'CIVIL'
        })
        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertTrue(Department.objects.filter(code='CIVIL').exists())

    def test_non_admin_add_department_fails(self):
        self.client.login(username="faculty1", password="password123")
        response = self.client.post(reverse('admin_add_department'), {
            'name': 'Civil Engineering',
            'code': 'CIVIL'
        })
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(Department.objects.filter(code='CIVIL').exists())

    def test_admin_add_course(self):
        self.client.login(username="admin1", password="password123")
        response = self.client.post(reverse('admin_add_course'), {
            'name': 'M.Tech ECE',
            'code': 'ECE-MTECH',
            'department': self.dept.id,
            'duration_years': 2
        })
        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertTrue(Course.objects.filter(code='ECE-MTECH').exists())

    def test_admin_add_faculty(self):
        self.client.login(username="admin1", password="password123")
        response = self.client.post(reverse('admin_add_faculty'), {
            'username': 'prof_jane',
            'email': 'jane@college.edu',
            'password': 'password123',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'faculty_id': 'FAC202',
            'department': self.dept.id,
            'designation': 'Professor',
            'phone_number': '1234567890',
            'qualification': 'Ph.D.'
        })
        self.assertRedirects(response, reverse('admin_dashboard'))
        user = CustomUser.objects.get(username='prof_jane')
        self.assertTrue(user.is_approved)
        self.assertEqual(user.role, 'FACULTY')
        self.assertTrue(FacultyProfile.objects.filter(faculty_id='FAC202').exists())

    def test_admin_add_student(self):
        self.client.login(username="admin1", password="password123")
        response = self.client.post(reverse('admin_add_student'), {
            'username': 'student_bob',
            'email': 'bob@college.edu',
            'password': 'password123',
            'first_name': 'Bob',
            'last_name': 'Jones',
            'student_id': 'STU303',
            'department': self.dept.id,
            'course': self.course.id,
            'roll_no': '26ECE12',
            'date_of_birth': '2005-05-12',
            'phone_number': '0987654321',
            'address': '456 Oak Ave'
        })
        self.assertRedirects(response, reverse('admin_dashboard'))
        user = CustomUser.objects.get(username='student_bob')
        self.assertTrue(user.is_approved)
        self.assertEqual(user.role, 'STUDENT')
        self.assertTrue(StudentProfile.objects.filter(student_id='STU303').exists())



