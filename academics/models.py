from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    duration_years = models.IntegerField(default=4)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')
    semester = models.IntegerField(default=1)
    # Faculty is nullable as it might be assigned later; resolved dynamically with FacultyProfile import
    faculty = models.ForeignKey('faculty.FacultyProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='subjects')
    credits = models.IntegerField(default=4)

    def __str__(self):
        return f"{self.name} ({self.code}) - Sem {self.semester}"

class Semester(models.Model):
    name = models.CharField(max_length=50) # e.g. Fall 2026, Spring 2027
    academic_year = models.CharField(max_length=20) # e.g. 2026-27
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.academic_year})"

class TimetableSlot(models.Model):
    DAYS_OF_WEEK = (
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='timetable_slots')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    classroom = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.subject.code} - {self.get_day_of_week_display()} ({self.start_time} - {self.end_time})"

class FeeRecord(models.Model):
    STATUS_CHOICES = (
        ('PAID', 'Paid'),
        ('UNPAID', 'Unpaid'),
        ('PENDING', 'Pending Approval'),
    )
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='fee_records')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='fee_records')
    amount = models.DecimalField(max_digits=10, decimal_places=2) # wait, max_digits=10, decimal_places=2 is standard
    due_date = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='UNPAID')
    payment_date = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.student.student_id} - {self.semester.name} - {self.status}"
