from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Message  # added

# --- Contact Form ---
class ContactForm(forms.ModelForm):
    """
    A contact form for users to send messages including their name,
    email, subject, and message body.
    """
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
            "name": forms.TextInput(attrs={
                'placeholder': 'Your Name',
                'class': 'form-input rounded-md border-gray-300',
            }),
            "email": forms.EmailInput(attrs={
                'placeholder': 'Your Email',
                'class': 'form-input rounded-md border-gray-300',
            }),
            "subject": forms.TextInput(attrs={
                'placeholder': 'Subject',
                'class': 'form-input rounded-md border-gray-300',
            }),
            "message": forms.Textarea(attrs={
                'placeholder': 'Your message here...',
                'rows': 5,
                'class': 'form-textarea rounded-md border-gray-300',
            }),
        }


# --- Registration Form ---
class RegistrationForm(UserCreationForm):
    """
    A registration form for creating new user accounts, extending from Django's
    built-in UserCreationForm.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Your Email',
            'class': 'form-input rounded-md border-gray-300',
        })
    )

    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'First Name',
            'class': 'form-input rounded-md border-gray-300',
        })
    )
    
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last Name',
            'class': 'form-input rounded-md border-gray-300',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        """
        Ensure the email is unique.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def save(self, commit=True):
        """
        Override save method to handle user creation.
        """
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
