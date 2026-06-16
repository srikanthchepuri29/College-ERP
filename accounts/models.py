from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('FACULTY', 'Faculty'),
        ('STUDENT', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    is_approved = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

    # Use email for unique login identifier if desired, but we'll support both email/username login
    REQUIRED_FIELDS = ['email']

    def save(self, *args, **kwargs):
        # Admin roles or superusers are approved by default
        if self.role == 'ADMIN' or self.is_superuser:
            self.is_approved = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"
