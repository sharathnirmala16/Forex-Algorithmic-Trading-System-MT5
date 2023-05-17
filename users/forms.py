from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 
from django.contrib.auth import authenticate
from .models import CustomUser

#used to register a new user
class CustomUserSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, label='', widget=forms.TextInput(attrs={
        'placeholder':'Email Address',
        'class' : 'app-form-control'
    }))

    first_name = forms.CharField(required=True, label='', widget=forms.TextInput(attrs={
        'placeholder':'First Name',
        'class' : 'app-form-control'
    }))

    last_name = forms.CharField(required=True, label='', widget=forms.TextInput(attrs={
        'placeholder':'Last Name',
        'class' : 'app-form-control'
    }))

    phone_number = forms.CharField(required=True, label='', widget=forms.TextInput(attrs={
        'placeholder':'Phone Number',
        'class' : 'app-form-control'
    }))

    demo_login = forms.CharField(required=True, label='', widget=forms.TextInput(attrs={
        'placeholder':'Demo Account Login',
        'class' : 'app-form-control'
    }))

    demo_password = forms.CharField(required=True, label='', widget=forms.PasswordInput(attrs={
        'placeholder':'Demo Account Password',
        'class' : 'app-form-control'
    }))

    demo_server = forms.CharField(required=True, label='', widget=forms.TextInput(attrs={
        'placeholder':'Demo Account Server',
        'class' : 'app-form-control'
    }))

    live_login = forms.CharField(required=True, label='', widget=forms.TextInput(attrs={
        'placeholder':'Live Account Login',
        'class' : 'app-form-control'
    }))

    live_password = forms.CharField(required=True, label='', widget=forms.PasswordInput(attrs={
        'placeholder':'Live Account Password',
        'class' : 'app-form-control'
    }))

    live_server = forms.CharField(required=True, label='', widget=forms.TextInput(attrs={
        'placeholder':'Live Account Server',
        'class' : 'app-form-control'
    }))

    password1 = forms.CharField(required=True, label='', widget=forms.PasswordInput(attrs={
        'placeholder':'PipProphet Password',
        'class' : 'app-form-control'
    }))
    
    password2 = forms.CharField(required=True, label='', widget=forms.PasswordInput(attrs={
        'placeholder':'Password Confirmation',
        'class' : 'app-form-control'
    }))

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone_number', 
                  'demo_login', 'demo_password', 'demo_server',
                  'live_login', 'live_password', 'live_server',
                  'password1', 'password2']

#used to login a user  
class CustomUserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Password'
    }))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        # Check if email and password are valid
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError('Invalid email or password')
            elif not user.is_active:
                raise forms.ValidationError('This account is inactive')
            cleaned_data['user'] = user
        return cleaned_data