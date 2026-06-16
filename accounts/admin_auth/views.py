from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from accounts.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken

# Hardcoded secret key for portfolio demo purposes
ADMIN_SECRET_KEY = "ERPADMIN2026"

def admin_login(request):
    if request.user.is_authenticated:
        if request.user.role == 'ADMIN':
            return redirect('admin_dashboard')
        logout(request)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.role != 'ADMIN':
                messages.error(request, "Access denied. This portal is for administrators only.")
            else:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                response = redirect('admin_dashboard')
                response.set_cookie('access_token', str(refresh.access_token), httponly=True)
                response.set_cookie('refresh_token', str(refresh), httponly=True)
                return response
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'accounts/admin_login.html')

def admin_register(request):
    if request.user.is_authenticated:
        logout(request)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        secret_code = request.POST.get('secret_code')
        
        if secret_code != ADMIN_SECRET_KEY:
            messages.error(request, "Invalid Admin Registration Secret Code.")
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
        else:
            try:
                # Create user with ADMIN role
                # Note: CustomUser's save() automatically sets is_approved=True for ADMIN role.
                CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    role='ADMIN'
                )
                messages.success(request, "Admin account registered successfully! Please log in.")
                return redirect('admin_login')
            except Exception as e:
                messages.error(request, f"Error registering admin: {str(e)}")

    return render(request, 'accounts/admin_register.html')

def user_logout(request):
    logout(request)
    response = redirect('home')
    # Clear JWT cookies
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    messages.success(request, "You have been logged out successfully.")
    return response
