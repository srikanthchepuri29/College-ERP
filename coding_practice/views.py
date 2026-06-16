import os
import sys
import subprocess
import tempfile
import time
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdminUserRole, IsFacultyUserRole, IsStudentUserRole
from coding_practice.models import CodingProblem, CodingSubmission, TestCase
from coding_practice.serializers import CodingProblemSerializer, CodingSubmissionSerializer

def evaluate_code(submission):
    code = submission.code
    problem = submission.problem
    testcases = TestCase.objects.filter(problem=problem)
    
    if not testcases.exists():
        submission.status = 'ACCEPTED'
        submission.save()
        return
        
    # Write student code to a temp file
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w', encoding='utf-8') as f:
        f.write(code)
        temp_file_path = f.name

    try:
        max_runtime = 0
        for tc in testcases:
            start_time = time.time()
            try:
                # Run subprocess using the active python interpreter (sys.executable)
                result = subprocess.run(
                    [sys.executable, temp_file_path],
                    input=tc.input_data,
                    text=True,
                    capture_output=True,
                    timeout=float(problem.time_limit_seconds)
                )
                runtime_ms = int((time.time() - start_time) * 1000)
                max_runtime = max(max_runtime, runtime_ms)
                
                if result.returncode != 0:
                    submission.status = 'RUNTIME_ERROR'
                    submission.runtime_ms = max_runtime
                    submission.save()
                    return
                    
                # Normalize and compare stdout vs expected output
                actual_out = result.stdout.strip().replace('\r\n', '\n')
                expected_out = tc.expected_output.strip().replace('\r\n', '\n')
                
                if actual_out != expected_out:
                    submission.status = 'WRONG_ANSWER'
                    submission.runtime_ms = max_runtime
                    submission.save()
                    return
                    
            except subprocess.TimeoutExpired:
                submission.status = 'TIME_LIMIT_EXCEEDED'
                submission.runtime_ms = int(problem.time_limit_seconds * 1000)
                submission.save()
                return
        
        # If all test cases pass
        submission.status = 'ACCEPTED'
        submission.runtime_ms = max_runtime
        submission.save()
        
    finally:
        # Always remove the temporary file to prevent pollution
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError:
                pass

class CodingProblemViewSet(viewsets.ModelViewSet):
    queryset = CodingProblem.objects.all().order_by('id')
    serializer_class = CodingProblemSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsFacultyUserRole() | IsAdminUserRole()]
        return [IsAuthenticated()]

class CodingSubmissionViewSet(viewsets.ModelViewSet):
    queryset = CodingSubmission.objects.all().order_by('-submitted_at')
    serializer_class = CodingSubmissionSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [IsStudentUserRole()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        student_profile = self.request.user.student_profile
        submission = serializer.save(student=student_profile, status='PENDING')
        evaluate_code(submission)

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN' or user.role == 'FACULTY':
            return CodingSubmission.objects.all()
        elif user.role == 'STUDENT' and hasattr(user, 'student_profile'):
            return CodingSubmission.objects.filter(student=user.student_profile)
        return CodingSubmission.objects.none()
