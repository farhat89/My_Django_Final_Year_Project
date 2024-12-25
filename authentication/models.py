# from django.db import models

# Create your models here.
# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator

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
        choices=ROLE_CHOICES,
        default='faculty'
    )
    last_login_attempt = models.DateTimeField(null=True, blank=True)
    login_attempts = models.IntegerField(default=0)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']

    class Meta:
        db_table = 'auth_user'
        
    def __str__(self):
        return self.email