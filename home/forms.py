from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Message


# CONTACT FORM (du har redan)
class ContactForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["name", "email", "subject", "message"]
        labels = {
            "name": "Your Name",
            "email": "Your Email",
            "subject": "Subject",
            "message": "Message",
        }
        widgets = {
            "name": forms.TextInput(attrs={'placeholder': 'Your Name', 'class': 'form-input rounded-md border-gray-300'}),
            "email": forms.EmailInput(attrs={'placeholder': 'Your Email', 'class': 'form-input rounded-md border-gray-300'}),
            "subject": forms.TextInput(attrs={'placeholder': 'Subject', 'class': 'form-input rounded-md border-gray-300'}),
            "message": forms.Textarea(attrs={'placeholder': 'Your message here...', 'rows': 5, 'class': 'form-textarea rounded-md border-gray-300'}),
        }


# NYTT: SIGNUP FORM
class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email',
            'class': 'form-input rounded-md border-gray-300'
        })
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-input rounded-md border-gray-300'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-input rounded-md border-gray-300'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-input rounded-md border-gray-300'}),
        }


# NYTT: LOGIN FORM
class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'class': 'form-input rounded-md border-gray-300'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-input rounded-md border-gray-300'
        })
    )