from django.db import models
from django.conf import settings

class LMSMaterial(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='lms_materials')
    uploaded_by = models.ForeignKey('faculty.FacultyProfile', on_delete=models.CASCADE, related_name='lms_materials')
    file = models.FileField(upload_to='lms_materials/', null=True, blank=True)
    external_link = models.URLField(max_length=500, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    download_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.title} - {self.subject.code}"
