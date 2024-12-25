# forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

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