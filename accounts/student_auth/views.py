from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from accounts.models import CustomUser
from students.models import StudentProfile
from academics.models import Department, Course
from rest_framework_simplejwt.tokens import RefreshToken

def student_login(request):
    if request.user.is_authenticated:
        if request.user.role == 'STUDENT':
            return redirect('student_dashboard')
        logout(request)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.role != 'STUDENT':
                messages.error(request, "Access denied. This portal is for students only.")
            elif not user.is_approved:
                messages.warning(request, "Your account is pending administrator approval.")
            else:
                login(request, user)
                # Generate JWT tokens for API usage
                refresh = RefreshToken.for_user(user)
                response = redirect('student_dashboard')
                # Set tokens in cookies so standard JS fetch requests can access them easily
                response.set_cookie('access_token', str(refresh.access_token), httponly=True)
                response.set_cookie('refresh_token', str(refresh), httponly=True)
                return response
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'accounts/student_login.html')

def student_register(request):
    if request.user.is_authenticated:
        logout(request)

    departments = Department.objects.all()
    courses = Course.objects.all()

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        
        # Profile specific fields
        student_id = request.POST.get('student_id')
        dept_id = request.POST.get('department')
        course_id = request.POST.get('course')
        roll_no = request.POST.get('roll_no')
        dob = request.POST.get('date_of_birth')
        phone = request.POST.get('phone_number')
        address = request.POST.get('address')
        
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
        elif StudentProfile.objects.filter(student_id=student_id).exists():
            messages.error(request, "Student ID already exists.")
        else:
            try:
                # Create user
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    role='STUDENT'
                )
                
                # Fetch related FK objects
                dept = Department.objects.get(id=dept_id) if dept_id else None
                course = Course.objects.get(id=course_id) if course_id else None
                
                # Create student profile (approved is default False in CustomUser model)
                StudentProfile.objects.create(
                    user=user,
                    student_id=student_id,
                    department=dept,
                    course=course,
                    roll_no=roll_no,
                    date_of_birth=dob if dob else None,
                    phone_number=phone,
                    admission_year=2026,
                    address=address
                )
                messages.success(request, "Registration successful! Your account is pending admin approval.")
                return redirect('student_login')
            except Exception as e:
                messages.error(request, f"Error registering student: {str(e)}")

    context = {
        'departments': departments,
        'courses': courses
    }
    return render(request, 'accounts/student_register.html', context)
