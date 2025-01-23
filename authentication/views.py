from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Sum
import json
from django.core.exceptions import ValidationError
from .forms import LoginForm, UserRegistrationForm
from .models import File, Collaboration, Notification
import mimetypes

def home(request):
    return render(request, 'authentication/home.html')

# Login Views
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
                        'redirect_url': reverse('authentication:dashboard')  # CHANGED LINE
                    })
                return redirect('authentication:dashboard')
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

# Register views
@csrf_protect
def register_view(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        # Print received data for debugging
        print("POST data:", request.POST)
        print("FILES:", request.FILES)
        
        form = UserRegistrationForm(request.POST, request.FILES)

        # Add these debug prints
        print("Department in POST data:", request.POST.get('department'))
        
        if not form.is_valid():
             # Add this debug print
            print("Department in cleaned_data:", form.cleaned_data.get('department'))
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
            # Add this debug print
            print("Saved user department:", user.department)
            
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

# Logout views
@login_required
@csrf_protect
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect(reverse('authentication:login'))
    return redirect(reverse('authentication:dashboard'))


# Dashboard Views
@login_required
def dashboard(request):
    """
    Main dashboard view showing storage usage, recent activities, and notifications
    """
    # Calculate storage statistics
    total_storage = 5 * 1024 * 1024 * 1024  # 5GB in bytes
    used_storage = File.objects.filter(user=request.user).aggregate(
        total=Sum('file_size'))['total'] or 0
    storage_percentage = (used_storage / total_storage) * 100

    # Get recent activities
    recent_activities = get_recent_activities(request.user)
    
    # Get notifications
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:5]

    # Get recent files
    recent_files = File.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]

    context = {
        'storage_used': {
            'used': used_storage,
            'total': total_storage,
            'percentage': storage_percentage,
            'used_formatted': format_file_size(used_storage),
            'total_formatted': format_file_size(total_storage)
        },
        'collaborations': Collaboration.objects.filter(user=request.user).count(),
        'recent_activities': recent_activities,
        'recent_files': recent_files,
        'notifications': notifications,
        'unread_notifications_count': notifications.count(),
    }
    
    return render(request, 'authentication/dashboard/dashboard.html', context)

# Files upload views
@login_required
@require_http_methods(["POST"])
def upload_file(request):
    """
    Handle file uploads and create associated notifications
    """
    try:
        files = request.FILES.getlist('files')
        uploaded_files = []
        
        for file in files:
            # Create File instance
            user_file = File.objects.create(
                user=request.user,
                name=file.name,
                file=file,
                file_size=file.size
            )
            
            # Create notification for the upload
            Notification.objects.create(
                user=request.user,
                message=f'Successfully uploaded file: {file.name}',
                icon='upload'
            )
            
            uploaded_files.append({
                'id': user_file.id,
                'name': user_file.name,
                'size': format_file_size(user_file.file_size),
                'created_at': user_file.created_at.isoformat()
            })
        
        return JsonResponse({
            'status': 'success',
            'files': uploaded_files
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def recent_activity(request):
    """
    API endpoint to get recent activities
    """
    activities = get_recent_activities(request.user)
    return JsonResponse({'activities': activities})

@login_required
def recent_files(request):
    """
    API endpoint to get recent files
    """
    files = File.objects.filter(user=request.user).order_by('-created_at')[:10]
    return JsonResponse({
        'files': [{
            'id': file.id,
            'name': file.name,
            'size': format_file_size(file.file_size),
            'created_at': file.created_at.isoformat(),
            'icon': get_file_icon_name(file.get_file_type())
        } for file in files]
    })

@login_required
def storage_usage(request):
    """
    API endpoint to get storage usage statistics
    """
    total_storage = 5 * 1024 * 1024 * 1024  # 5GB in bytes
    used_storage = File.objects.filter(user=request.user).aggregate(
        total=Sum('file_size'))['total'] or 0
    storage_percentage = (used_storage / total_storage) * 100
    
    return JsonResponse({
        'usage': {
            'used': format_file_size(used_storage),
            'total': format_file_size(total_storage),
            'percentage': storage_percentage
        }
    })

def get_recent_activities(user):
    """Helper function to get user's recent activities"""
    recent_files = File.objects.filter(user=user).order_by('-modified_at')[:5]
    
    activities = []
    for file in recent_files:
        file_type = file.get_file_type()
        icon = get_file_icon_name(file_type)  
        activities.append({
            'description': f"Updated file: {file.name}",
            'timestamp': file.modified_at,
            'icon': icon,
            'type': 'file'  # Add type for styling
        })
    
    recent_collabs = Collaboration.objects.filter(user=user).order_by('-created_at')[:3]
    for collab in recent_collabs:
        activities.append({
            'description': f"Started collaboration on: {collab.file.name}",
            'timestamp': collab.created_at,
            'icon': 'users',  # Font Awesome icon name
            'type': 'collaboration'
        })
    
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    return activities[:5]  # Return only the 5 most recent activities

def get_file_icon_name(extension):
    """Map file extensions to Font Awesome icon names"""
    icon_map = {
        'pdf': 'file-pdf',
        'doc': 'file-word',
        'docx': 'file-word',
        'xls': 'file-excel',
        'xlsx': 'file-excel',
        'ppt': 'file-powerpoint',
        'pptx': 'file-powerpoint',
        'jpg': 'file-image',
        'jpeg': 'file-image',
        'png': 'file-image',
        'Audio': 'file-audio',
        'mp3': 'file-audio',
        'mp4': 'file-video',
        'avi': 'file-video',
         'Video': 'file-video',
        'gif': 'file-image',
        'zip': 'file-archive',
        'rar': 'file-archive',
        'html': 'file-code',
        'css': 'file-code',
        'js': 'file-code',
        'py': 'file-code',
        'txt': 'file-alt'
    }
    return icon_map.get(extension.lower(), 'file')  # Default to 'file' if extension not found

def format_file_size(size_in_bytes):
    """
    Helper function to format file sizes
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.1f} TB"

@login_required
def mark_notification_read(request, notification_id):
    """
    AJAX view to mark a notification as read
    """
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False}, status=404)

@login_required
def mark_all_notifications_read(request):
    """
    AJAX view to mark all notifications as read
    """
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})

# profile views
@login_required
def profile_view(request):
    """View for displaying and updating user profile"""
    user = request.user

    if request.method == 'POST':
        if 'profile_picture' in request.FILES:
            try:
                request.user.profile_picture = request.FILES['profile_picture']
                request.user.save()
                messages.success(request, 'Profile picture updated successfully!')
            except ValidationError as e:
                messages.error(request, str(e))
        return redirect('authentication:profile')
    
    context = {
        'user': request.user,
    }
    return render(request, 'authentication/dashboard/profile.html', context)

# Search files views
@login_required
def search_files(request):
    """View for searching files"""
    query = request.GET.get('query', '')
    if query:
        files = File.objects.filter(
            user=request.user,
            name__icontains=query
        ).order_by('-created_at')
    else:
        files = File.objects.filter(user=request.user).order_by('-created_at')[:5]

    return JsonResponse({
        'files': [{
            'id': file.id,
            'name': file.name,
            'size': format_file_size(file.file_size),
            'created_at': file.created_at.strftime('%Y-%m-%d %H:%M')
        } for file in files]
    })