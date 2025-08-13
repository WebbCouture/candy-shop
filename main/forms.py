from django import forms

class ContactForm(forms.Form):
    """
    A contact form for users to send messages including their name,
    email, subject, and message body.
    """
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
