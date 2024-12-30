# forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from PIL import Image
import magic
import re

User = get_user_model()

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@university.edu'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '********'
        })
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    remember_me = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        role = cleaned_data.get('role')

        if email and role:
            user = User.objects.filter(email=email).first()
            if not user:
                raise ValidationError('Invalid email or password')
            if user.role != role:
                raise ValidationError('Invalid role selected for this user')
        
        return cleaned_data


class UserRegistrationForm(forms.ModelForm):
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name'
        })
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        }),
        label="Confirm Password"
    )
    
    class Meta:
        model = User
        fields = ['email', 'password', 'role', 'profile_picture']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@university.edu'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            }),
            'role': forms.Select(attrs={
                'class': 'form-select'
            }),
            'profile_picture': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            }),
        }

    def clean_password(self):
        """
        Validates that the password meets all required criteria:
        - At least 8 characters long
        - Contains at least one uppercase letter
        - Contains at least one lowercase letter
        - Contains at least one number
        - Contains at least one special character (@$!%*?&)
        """
        password = self.cleaned_data.get('password')
        
        # Check password length
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        
        # Check password complexity using regex
        regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not re.match(regex, password):
            raise ValidationError(
                'Password must include at least 8 characters, one uppercase letter, '
                'one lowercase letter, one number, and one special character (@$!%*?&).'
            )
        
        return password

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords don't match.")
        return confirm_password

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            # Check file type
            mime = magic.from_buffer(profile_picture.read(), mime=True)
            if mime not in ['image/jpeg', 'image/png']:
                raise ValidationError('Please upload a valid JPEG or PNG image.')
            
            # Reset file pointer
            profile_picture.seek(0)
            
            # Check dimensions
            img = Image.open(profile_picture)
            if img.height < 100 or img.width < 100:
                raise ValidationError('Image must be at least 100x100 pixels.')
                
            return profile_picture
        return None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Set username to email
        user.set_password(self.cleaned_data['password'])  # Hash the password
        
        # Handle full name
        full_name = self.cleaned_data.get('full_name', '').split()
        if full_name:
            user.first_name = full_name[0]
            user.last_name = ' '.join(full_name[1:]) if len(full_name) > 1 else ''
        
        if commit:
            user.save()
        return user