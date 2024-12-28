
# Create your views here.
# views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
import re
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from django.http import JsonResponse
from .forms import LoginForm, UserRegistrationForm
import json

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = json.loads(request.body)
            form = LoginForm(data)
        else:
            form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            role = form.cleaned_data.get('role')
            remember_me = form.cleaned_data.get('remember_me')

            user = authenticate(request, username=email, password=password)
            
            if user is not None and user.role == role:
                if not remember_me:
                    request.session.set_expiry(0)
                
                login(request, user)
                user.last_login = timezone.now()
                user.login_attempts = 0
                user.save()

                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'redirect_url': '/dashboard/'
                    })
                return redirect('dashboard')
            else:
                user = User.objects.filter(email=email).first()
                if user:
                    user.login_attempts += 1
                    user.last_login_attempt = timezone.now()
                    user.save()

                error_message = 'Invalid credentials or role'
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': error_message
                    }, status=400)
                messages.error(request, error_message)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': form.errors
                }, status=400)
            messages.error(request, form.errors)

    else:
        form = LoginForm()

    return render(request, 'authentication/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('authentication:login')

@csrf_protect
def register_view(request):
    if request.method == 'POST':
        # Check if it's an AJAX request
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        # Create a form instance with POST data and files
        form = UserRegistrationForm(request.POST, request.FILES)
        
        # Process form data
        if form.is_valid():
            try:
                # Create user instance but don't save yet
                user = form.save(commit=False)
                
                # Add additional fields
                user.first_name = request.POST.get('full_name')
                user.department = request.POST.get('department')
                
                # Save the user
                user.save()
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Registration successful! Please log in.',
                        'redirect_url': '/auth/login/'
                    })
                
                messages.success(request, "Registration successful! Please log in.")
                return redirect('authentication:login')
                
            except Exception as e:
                error_message = str(e)
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': error_message
                    }, status=400)
                messages.error(request, error_message)
        else:
            # If form is invalid, handle errors
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': form.errors
                }, status=400)
            messages.error(request, "Please correct the errors below.")
    else:
        # If GET request, create empty form
        form = UserRegistrationForm()

    # Render the registration template with the form
    context = {
        'form': form,
        'password_pattern': r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    }
    return render(request, 'authentication/register.html', context)