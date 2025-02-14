from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()  # Get active user model
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, Q
import json
from django.core.exceptions import ValidationError
from .forms import LoginForm, UserRegistrationForm, CollaborationForm
from .models import File, Collaboration, Notification, SharedFile, CollaborationActivity
from django.core.paginator import Paginator
from django.http import HttpResponse, FileResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.conf import settings
import os
import mimetypes
from django.template.loader import render_to_string
import logging
from django.contrib.auth.password_validation import validate_password

# Configure logger
logger = logging.getLogger(__name__)

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
            'description': f"Started collaboration on: {collab.file.name if collab.file else 'Untitled File'}",
            'timestamp': collab.created_at,
            'icon': 'users', #Font awesome icon name
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

# my_files views
@login_required
def my_files(request):
    # Get the list of files for the current user
    files = File.objects.filter(user=request.user).order_by('-created_at')
    
    # Paginate the files (10 per page)
    paginator = Paginator(files, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Format file data for the template
    formatted_files = [{
        'id': file.id,
        'name': file.name,
        'size': format_file_size(file.file_size),
        'modified': file.modified_at.strftime('%b %d, %Y')
    } for file in page_obj]

    context = {
        'files': formatted_files,
        'storage_used': {
            'used': File.objects.filter(user=request.user).aggregate(total=Sum('file_size'))['total'] or 0,
            'total': 5 * 1024 * 1024 * 1024,  # 5GB in bytes
            'percentage': (File.objects.filter(user=request.user).aggregate(total=Sum('file_size'))['total'] or 0) / (5 * 1024 * 1024 * 1024) * 100,
            'used_formatted': format_file_size(File.objects.filter(user=request.user).aggregate(total=Sum('file_size'))['total'] or 0),
            'total_formatted': format_file_size(5 * 1024 * 1024 * 1024)
        }
    }

    return render(request, 'authentication/dashboard/my_files.html', context)

# File download and delete views
@login_required
def download_file(request, file_id):
    try:
        file = File.objects.get(id=file_id)
        
        # Check if the user owns the file or has been granted access
        if file.user == request.user or SharedFile.objects.filter(file=file, shared_with=request.user).exists():
            file_path = file.file.path

            if os.path.exists(file_path):
                # Use FileResponse to stream the file to the user
                response = FileResponse(open(file_path, 'rb'))
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
            else:
                return JsonResponse({'success': False, 'message': 'File not found.'}, status=404)
        else:
            return JsonResponse({'success': False, 'message': 'You do not have permission to access this file.'}, status=403)
    except File.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'File not found.'}, status=404)

@login_required
@require_http_methods(["DELETE"])
def delete_file(request, file_id):
    try:
        file = File.objects.get(id=file_id, user=request.user)
        file_path = file.file.path

        # Delete the file from the file system
        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete the file record from the database
        file.delete()

        return JsonResponse({'success': True})
    except File.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'File not found.'}, status=404)
    
#share file views
@login_required
@require_http_methods(["POST"])
def share_file(request, file_id):
    try:
        file = File.objects.get(id=file_id, user=request.user)
        data = json.loads(request.body)
        emails = data.get('emails', [])
        access_permission = data.get('access_permission', 'view')

        if not emails:
            return JsonResponse({'success': False, 'message': 'No recipients provided.'}, status=400)

        # Validate emails and fetch corresponding users
        User = get_user_model()
        recipients = []
        for email in emails:
            try:
                user = User.objects.get(email=email)
                recipients.append(user)
            except User.DoesNotExist:
                logger.warning(f"User with email {email} does not exist.")
                continue

        if not recipients:
            return JsonResponse({'success': False, 'message': 'No valid recipients found.'}, status=400)

        # Create SharedFile records
        for recipient in recipients:
            SharedFile.objects.create(
                file=file,
                shared_by=request.user,
                shared_with=recipient,
                permission=access_permission
            )

        return JsonResponse({'success': True})
    except File.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'File not found.'}, status=404)
    except Exception as e:
        logger.error(f"Error sharing file: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
def shared_files(request):
    # Get files shared by the current user
    shared_by_me = SharedFile.objects.filter(shared_by=request.user)
    
    # Get files shared with the current user
    shared_with_me = SharedFile.objects.filter(shared_with=request.user)
    
    # Calculate the total unique shared files
    all_shared_files = SharedFile.objects.filter(
        Q(shared_by=request.user) | Q(shared_with=request.user)
    ).distinct()
    
    total_shared_files = all_shared_files.count()

    context = {
        'shared_by_me': shared_by_me,
        'shared_with_me': shared_with_me,
        'total_shared_files': total_shared_files,
    }
    return render(request, 'authentication/dashboard/shared_files.html', context)

@login_required
@require_http_methods(["POST"])
def remove_shared_access(request, shared_file_id):
    try:
        shared_file = SharedFile.objects.get(id=shared_file_id, shared_by=request.user)
        shared_file.delete()
        return JsonResponse({'success': True})
    except SharedFile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Shared file not found.'}, status=404)
    
#view file views
@login_required
def view_file(request, file_id):
    # Fetch the file from the database
    file = get_object_or_404(File, id=file_id, user=request.user)
    
    # Render a template to display the file details
    return render(request, 'authentication/dashboard/view_file.html', {'file': file})

#view file views in browser
@login_required
def view_file(request, file_id):
    # Fetch the file from the database
    file = get_object_or_404(File, id=file_id, user=request.user)
    
    # Get the file path
    file_path = file.file.path
    
    # Check if the file exists
    if not os.path.exists(file_path):
        return HttpResponse("File not found.", status=404)
    
    # Determine the MIME type of the file
    mime_type, _ = mimetypes.guess_type(file_path)
    
    # If the MIME type is unknown, default to 'application/octet-stream'
    if mime_type is None:
        mime_type = 'application/octet-stream'
    
    # Use FileResponse to stream the file content
    response = FileResponse(open(file_path, 'rb'), content_type=mime_type)
    
    # Set the Content-Disposition header to inline (for viewing in the browser)
    response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
    
    # Enable range requests for large files (e.g., videos)
    response['Accept-Ranges'] = 'bytes'
    return response
    
# api_shared_files views
@login_required
def api_shared_files(request):
    page = int(request.GET.get('page', 1))
    per_page = 10
    shared_by_me = SharedFile.objects.filter(shared_by=request.user)
    shared_with_me = SharedFile.objects.filter(shared_with=request.user)
    shared_files = list(shared_by_me) + list(shared_with_me)
    shared_files = sorted(shared_files, key=lambda x: x.shared_at, reverse=True)
    paginator = Paginator(shared_files, per_page)
    page_obj = paginator.get_page(page)
    
    files = [{
        'id': sf.file.id,
        'name': sf.file.name,
        'shared_at': sf.shared_at.strftime('%b %d, %Y'),
    } for sf in page_obj]
    
    return JsonResponse({'files': files})    

#collaborations views
@login_required
def collaborations(request):
    # Get active user model at function level
    User = get_user_model()  # Fresh reference to the active user model
    # Statistics
    total_collaborations = Collaboration.objects.filter(user=request.user).count()
    active_projects = Collaboration.objects.filter(user=request.user, status='active').count()
    
    # Get unique collaborators across all collaborations
    collaborator_ids = Collaboration.objects.filter(user=request.user)\
        .values_list('participants', flat=True).distinct()
    total_collaborators = User.objects.filter(id__in=collaborator_ids).count()

    # Active collaborations
    collaborations = Collaboration.objects.filter(user=request.user)\
        .prefetch_related('participants').order_by('-updated_at')

    # Recent activities
    recent_activities = CollaborationActivity.objects.filter(
        collaboration__user=request.user
    ).order_by('-created_at')[:10]

    context = {
        'total_collaborations': total_collaborations,
        'active_projects': active_projects,
        'total_collaborators': total_collaborators,
        'collaborations': collaborations,
        'recent_activities': recent_activities
    }
    return render(request, 'authentication/dashboard/collaborations.html', context)

#api_collaborations views
@login_required
def api_collaborations(request):
    # Get request parameters
    status = request.GET.get('status', 'all')
    sort = request.GET.get('sort', 'updated')
    offset = int(request.GET.get('offset', 0))
    limit = 5

    # Base queryset
    collaborations = Collaboration.objects.filter(user=request.user)\
        .prefetch_related('participants')

    # Apply status filter
    if status != 'all':
        collaborations = collaborations.filter(status=status)

    # Apply sorting
    sort_mapping = {
        'updated': '-updated_at',
        'created': '-created_at',
        'name': 'title'
    }
    collaborations = collaborations.order_by(sort_mapping.get(sort, '-updated_at'))

    # Apply pagination
    collaborations = collaborations[offset:offset+limit]

    # Render HTML partial
    html = render_to_string('authentication/partials/collaboration_items.html', {
        'collaborations': collaborations
    })

    return JsonResponse({'html': html})

@login_required
def api_collaboration_activities(request):
    offset = int(request.GET.get('offset', 0))
    limit = 5
    
    activities = CollaborationActivity.objects.filter(
        collaboration__user=request.user
    ).order_by('-created_at')[offset:offset+limit]
    
    html = render_to_string('authentication/partials/activity_items.html', {
        'activities': activities
    })
    
    return JsonResponse({'html': html})

# new endpoint for combined filtering/sorting
@login_required
def api_filtered_collaborations(request):
    status = request.GET.get('status', 'all')
    sort = request.GET.get('sort', 'updated')
    
    collaborations = Collaboration.objects.filter(user=request.user)\
        .prefetch_related('participants')

    if status != 'all':
        collaborations = collaborations.filter(status=status)

    sort_mapping = {
        'updated': '-updated_at',
        'created': '-created_at',
        'name': 'title'
    }
    collaborations = collaborations.order_by(sort_mapping.get(sort, '-updated_at'))

    html = render_to_string('authentication/partials/collaboration_items.html', {
        'collaborations': collaborations
    })

    return JsonResponse({'html': html})

@login_required
def create_collaboration(request):
    if request.method == 'POST':
        form = CollaborationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                # Handle file assignment
                file_instance = None
                if form.cleaned_data.get('existing_file'):
                    file_instance = form.cleaned_data['existing_file']
                elif form.cleaned_data.get('new_file'):
                    uploaded_file = form.cleaned_data['new_file']
                    file_instance = File.objects.create(
                        user=request.user,
                        name=uploaded_file.name,
                        file=uploaded_file,
                        file_size=uploaded_file.size
                    )
                
                # Create collaboration
                collaboration = form.save(commit=False)
                collaboration.user = request.user
                collaboration.file = file_instance
                collaboration.save()
                form.save_m2m()  # Save participants
                
                # Add owner as participant if not already included
                if request.user not in collaboration.participants.all():
                    collaboration.participants.add(request.user)

                return JsonResponse({
                    'status': 'success',
                    'redirect': reverse('authentication:collaboration_session', args=[collaboration.channel_group])
                })

            except Exception as e:
                logger.error(f"Collaboration creation error: {str(e)}")
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        return JsonResponse({'status': 'error', 'errors': form.errors.get_json_data()}, status=400)
    return JsonResponse({'status': 'invalid_request'}, status=400)

@login_required
def search_users(request):
    search_term = request.GET.get('q', '')
    users = User.objects.filter(
        Q(email__icontains=search_term) |
        Q(first_name__icontains=search_term) |
        Q(last_name__icontains=search_term)
    ).exclude(id=request.user.id)[:10]

    results = [{
        'id': user.id,
        'text': f"{user.get_full_name() or user.email} ({user.email})"
    } for user in users]

    return JsonResponse({'users': results})

@login_required
def collaboration_session(request, collab_uuid):
    # Fetch the collaboration object using the UUID and ensure the user is a participant
    collaboration = get_object_or_404(
        Collaboration,
        channel_group=collab_uuid,
        participants=request.user  # Ensuring user is a participant
    )

    # Read the file content if a file is associated with the collaboration
    file_content = ""
    if collaboration.file and collaboration.file.file:
        try:
            # Read file as binary and decode with UTF-8, replace errors
            with collaboration.file.file.open('rb') as f:
                file_content = f.read().decode('utf-8', errors='replace')
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            file_content = "Error: Unable to display file content"

    # Pass the collaboration object, file content, and UUID to the template
    return render(request, 'authentication/dashboard/session.html', {
        'collaboration': collaboration,
        'file_content': file_content,
        'collab_uuid': collab_uuid  # Pass the UUID to the template
    })

#settings views
@login_required
def settings_view(request):
    if request.method == 'POST':
        # Handle profile picture update
        if 'profile_picture' in request.FILES:
            try:
                request.user.profile_picture = request.FILES['profile_picture']
                request.user.save()
                messages.success(request, 'Profile picture updated successfully!')
            except ValidationError as e:
                messages.error(request, str(e))
            return redirect('authentication:settings')

        # Handle password change
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        
        if current_password and new_password:
            if not request.user.check_password(current_password):
                return JsonResponse({'success': False, 'error': 'Current password is incorrect'})
            
            try:
                validate_password(new_password, user=request.user)
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                return JsonResponse({'success': True})
            except ValidationError as e:
                return JsonResponse({'success': False, 'error': ', '.join(e.messages)})

    return render(request, 'authentication/dashboard/settings.html')

@login_required
@require_http_methods(["POST"])
def update_notification_prefs(request):
    try:
        data = json.loads(request.body)
        setting = data.get('setting')
        value = data.get('value')
        
        if setting == 'emailNotifications':
            request.user.email_notifications = value
        elif setting == 'fileUpdates':
            request.user.file_updates = value
        
        request.user.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)