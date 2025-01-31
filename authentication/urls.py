# urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'authentication'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Password Reset URLs
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='authentication/password_reset_form.html',
             success_url='/auth/password_reset/done/',  # Add this line
             email_template_name='authentication/password_reset_email.html',
             subject_template_name='authentication/password_reset_subject.txt'
         ),
         name='password_reset'),
    
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='authentication/password_reset_done.html'
         ),
         name='password_reset_done'),  # This name must match exactly
    
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='authentication/password_reset_confirm.html',
             success_url='/auth/reset/done/' 
         ),
         name='password_reset_confirm'),
    
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='authentication/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('notifications/mark-read/<int:notification_id>/', 
         views.mark_notification_read, name='mark_notification_read'),
         
    path('api/notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),

    path('api/upload/', views.upload_file, name='upload_file'),

    path('api/recent-activity/', views.recent_activity, name='recent_activity'),
    
    path('api/recent-files/', views.recent_files, name='recent_files'),
    
    path('api/storage-usage/', views.storage_usage, name='storage_usage'),
    path('api/shared-files/', views.api_shared_files, name='api_shared_files'),

    path('profile/', views.profile_view, name='profile'),
    path('search-files/', views.search_files, name='search_files'),
    path('my-files/', views.my_files, name='my_files'),
    path('download-file/<int:file_id>/', views.download_file, name='download_file'),
    path('delete-file/<int:file_id>/', views.delete_file, name='delete_file'),
    path('share-file/<int:file_id>/', views.share_file, name='share_file'),
    path('shared-files/', views.shared_files, name='shared_files'),
    path('remove-shared-access/<int:shared_file_id>/', views.remove_shared_access, name='remove_shared_access'),
    path('files/<int:file_id>/', views.view_file, name='view_file'),
    path('collaborations/', views.collaborations, name='collaborations'),
    path('api/collaborations/', views.api_collaborations, name='api_collaborations'),
    path('api/collaborations/filter/', views.api_filtered_collaborations, name='api_filtered_collaborations'),
    path('api/collaboration-activities/', views.api_collaboration_activities, name='api_collaboration_activities'),

         
]