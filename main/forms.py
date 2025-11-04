from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Product

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


# --- Product Form for CRUD ---
class ProductForm(forms.ModelForm):
    """Form for shop owner to add or edit products."""
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input w-full border rounded-md px-3 py-2'}),
            'description': forms.Textarea(attrs={'class': 'form-input w-full border rounded-md px-3 py-2'}),
            'price': forms.NumberInput(attrs={'class': 'form-input w-full border rounded-md px-3 py-2'}),
            'image_url': forms.URLInput(attrs={'class': 'form-input w-full border rounded-md px-3 py-2'}),
        }
