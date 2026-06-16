from django.db import models

class ExamSchedule(models.Model):
    EXAM_TYPES = (
        ('INTERNAL', 'Internal Assessment'),
        ('EXTERNAL', 'Semester End Exam'),
    )
    name = models.CharField(max_length=100) # e.g. Midterm 1, End Semester Exam
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='exams')
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPES, default='INTERNAL')
    date = models.DateField()
    max_marks = models.IntegerField(default=100)

    def __str__(self):
        return f"{self.name} - {self.subject.code}"

class Result(models.Model):
    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='results')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5) # e.g. A+, B, F
    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ('exam_schedule', 'student')

    def __str__(self):
        return f"{self.student.student_id} - {self.exam_schedule.name} - Marks: {self.marks_obtained}/{self.exam_schedule.max_marks}"

class ExamSubmission(models.Model):
    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='exam_submissions')
    answers = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('exam_schedule', 'student')

    def __str__(self):
        return f"Submission: {self.student.student_id} - {self.exam_schedule.name}"
