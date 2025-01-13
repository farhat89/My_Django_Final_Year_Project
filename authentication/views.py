from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse
import json
from .forms import LoginForm, UserRegistrationForm

def home(request):
    return render(request, 'authentication/home.html')

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        if is_ajax:
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

                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'redirect_url': reverse('dashboard')
                    })
                return redirect('dashboard')
            else:
                error_message = 'Invalid credentials or the selected role does not match your account role.'
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': error_message
                    }, status=400)
                messages.error(request, error_message)
        else:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': form.errors
                }, status=400)
            messages.error(request, form.errors)

    else:
        form = LoginForm()

    return render(request, 'authentication/login.html', {'form': form})

@csrf_protect
def register_view(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        # Print received data for debugging
        print("POST data:", request.POST)
        print("FILES:", request.FILES)
        
        form = UserRegistrationForm(request.POST, request.FILES)
        
        if not form.is_valid():
            print("Form errors:", form.errors)
            error_response = {
                'success': False,
                'message': {field: str(errors[0]) for field, errors in form.errors.items()}
            }
            if is_ajax:
                return JsonResponse(error_response, status=400)
            messages.error(request, "Please correct the errors below.")
            return render(request, 'authentication/register.html', {'form': form})
        
        try:
            user = form.save()  # This will now handle username creation
            
            success_message = 'Registration successful! Please log in.'
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': success_message,
                    'redirect_url': reverse('authentication:login')
                })
            
            messages.success(request, success_message)
            return redirect('authentication:login')
            
        except Exception as e:
            print("Registration error:", str(e))
            error_message = "An unexpected error occurred during registration. Please try again later."
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': {'general': error_message}
                }, status=400)
            messages.error(request, error_message)
    
    else:
        form = UserRegistrationForm()
    
    return render(request, 'authentication/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect(reverse('authentication:login'))

