from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from accounts.models import CustomUser
from faculty.models import FacultyProfile
from academics.models import Department
from rest_framework_simplejwt.tokens import RefreshToken

def faculty_login(request):
    if request.user.is_authenticated:
        if request.user.role == 'FACULTY':
            return redirect('faculty_dashboard')
        logout(request)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.role != 'FACULTY':
                messages.error(request, "Access denied. This portal is for faculty only.")
            elif not user.is_approved:
                messages.warning(request, "Your account is pending administrator approval.")
            else:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                response = redirect('faculty_dashboard')
                response.set_cookie('access_token', str(refresh.access_token), httponly=True)
                response.set_cookie('refresh_token', str(refresh), httponly=True)
                return response
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'accounts/faculty_login.html')

def faculty_register(request):
    if request.user.is_authenticated:
        logout(request)

    departments = Department.objects.all()

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        
        # Profile specific fields
        faculty_id = request.POST.get('faculty_id')
        dept_id = request.POST.get('department')
        designation = request.POST.get('designation')
        phone = request.POST.get('phone_number')
        qualification = request.POST.get('qualification')
        
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
        elif FacultyProfile.objects.filter(faculty_id=faculty_id).exists():
            messages.error(request, "Faculty ID already registered.")
        else:
            try:
                # Create user
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    role='FACULTY'
                )
                
                # Fetch related FK department
                dept = Department.objects.get(id=dept_id) if dept_id else None
                
                # Create faculty profile
                FacultyProfile.objects.create(
                    user=user,
                    faculty_id=faculty_id,
                    department=dept,
                    designation=designation,
                    phone_number=phone,
                    qualification=qualification
                )
                messages.success(request, "Registration successful! Your account is pending admin approval.")
                return redirect('faculty_login')
            except Exception as e:
                messages.error(request, f"Error registering faculty: {str(e)}")

    context = {
        'departments': departments
    }
    return render(request, 'accounts/faculty_register.html', context)
