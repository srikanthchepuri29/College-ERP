from django.test import TestCase
from accounts.models import CustomUser

class AuthenticationTests(TestCase):
    def test_admin_auto_approval(self):
        # Admin users should be auto-approved by default
        user = CustomUser.objects.create_user(
            username="testadmin",
            email="testadmin@college.edu",
            password="testpassword123",
            role="ADMIN"
        )
        self.assertTrue(user.is_approved)

    def test_student_pending_approval(self):
        # Student users should require admin approval (is_approved=False by default)
        user = CustomUser.objects.create_user(
            username="teststudent",
            email="teststudent@college.edu",
            password="testpassword123",
            role="STUDENT"
        )
        self.assertFalse(user.is_approved)
