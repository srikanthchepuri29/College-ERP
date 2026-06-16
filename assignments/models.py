from django.db import models
from django.conf import settings

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='assignments')
    created_by = models.ForeignKey('faculty.FacultyProfile', on_delete=models.CASCADE, related_name='assignments')
    deadline = models.DateTimeField()
    max_marks = models.IntegerField(default=100)
    file = models.FileField(upload_to='assignments/', null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.subject.code}"

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='assignment_submissions')
    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    is_evaluated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.student_id} - {self.assignment.title}"
