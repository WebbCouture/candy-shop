from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# --- Contact Form ---
class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=True,
        label="Your Name",
        widget=forms.TextInput(attrs={
            'placeholder': 'Your Name',
            'class': 'form-input rounded-md border-gray-300',
        })
    )
    email = forms.EmailField(
        required=True,
        label="Your Email",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Your Email',
            'class': 'form-input rounded-md border-gray-300',
        })
    )
    subject = forms.CharField(
        max_length=150,
        required=True,
        label="Subject",
        widget=forms.TextInput(attrs={
            'placeholder': 'Subject',
            'class': 'form-input rounded-md border-gray-300',
        })
    )
    message = forms.CharField(
        required=True,
        label="Message",
        widget=forms.Textarea(attrs={
            'placeholder': 'Your message here...',
            'rows': 5,
            'class': 'form-textarea rounded-md border-gray-300',
        })
    )

# --- Signup Form ---
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user
