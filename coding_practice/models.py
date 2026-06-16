from django.db import models
from django.conf import settings

class CodingProblem(models.Model):
    DIFFICULTY_CHOICES = (
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='Easy')
    input_format = models.TextField()
    output_format = models.TextField()
    sample_input = models.TextField()
    sample_output = models.TextField()
    time_limit_seconds = models.IntegerField(default=2)
    memory_limit_mb = models.IntegerField(default=256)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_problems')

    def __str__(self):
        return f"{self.title} ({self.difficulty})"

class TestCase(models.Model):
    problem = models.ForeignKey(CodingProblem, on_delete=models.CASCADE, related_name='testcases')
    input_data = models.TextField()
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False)

    def __str__(self):
        return f"TestCase for {self.problem.title} (Sample: {self.is_sample})"

class CodingSubmission(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('WRONG_ANSWER', 'Wrong Answer'),
        ('COMPILE_ERROR', 'Compile Error'),
        ('TIME_LIMIT_EXCEEDED', 'Time Limit Exceeded'),
        ('RUNTIME_ERROR', 'Runtime Error'),
    )
    problem = models.ForeignKey(CodingProblem, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='coding_submissions')
    code = models.TextField()
    language = models.CharField(max_length=20, default='python')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING')
    runtime_ms = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.student_id} - {self.problem.title} - {self.status}"
