# from django.db import models

# Create your models here.
# models.py
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from PIL import Image
import os

# Validator to ensure the image size does not exceed the limit
def validate_image_size(image):
    filesize = image.size
    megabyte_limit = 2.0  # Maximum allowed size is 2 MB
    if filesize > megabyte_limit * 1024 * 1024:
        raise ValidationError(f"Image size cannot exceed {megabyte_limit}MB")

# Function to generate the upload path for profile pictures
def profile_picture_path(instance, filename):
    # Save profile pictures under: media/profile_pictures/<user_id>/<filename>
    return f"profile_pictures/{instance.id}/{filename}"

# Custom User model with profile picture and additional fields
class User(AbstractUser):
    ROLE_CHOICES = [
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
        ('external', 'External Partner'),
    ]
    
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        error_messages={
            'unique': 'A user with this email already exists.',
        }
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
        # default='faculty'
    )
    last_login_attempt = models.DateTimeField(null=True, blank=True)
    login_attempts = models.IntegerField(default=0)

    # Profile picture field
    profile_picture = models.ImageField(
        upload_to=profile_picture_path,
        validators=[validate_image_size],
        null=True,
        blank=True,
        help_text="Upload a JPEG or PNG image (max size: 2MB)."
    )

    DEPARTMENT_CHOICES = [
        ('Computer Science', 'Computer Science'),
        ('Software Engineering', 'Software Engineering'),
        ('Cyber Security', 'Cyber Security'),
    ]

    department = models.CharField(
        max_length=100,
        choices=DEPARTMENT_CHOICES,
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return self.email

    # Override save method to resize profile picture if necessary
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.profile_picture:
            img = Image.open(self.profile_picture.path)
            max_size = (300, 300)  # Resize image to a maximum of 300x300
            if img.height > max_size[1] or img.width > max_size[0]:
                img.thumbnail(max_size)
                img.save(self.profile_picture.path)

    # Override delete method to remove profile picture file when user is deleted
    def delete(self, *args, **kwargs):
        if self.profile_picture and os.path.isfile(self.profile_picture.path):
            os.remove(self.profile_picture.path)
        super().delete(*args, **kwargs)

class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='files/')
    file_size = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Collaboration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    icon = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.message[:50]}"