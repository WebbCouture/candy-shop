from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required  # Added import

from .forms import ContactForm
from .models import Product

# Home page - shows latest products
def home(request):
    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())

    latest_products = Product.objects.all().order_by('-id')[:3]

    return render(request, 'main/home.html', {
        'cart_count': cart_count,
        'latest_products': latest_products,
    })

# Product list + search
def product_list(request):
    query = request.GET.get('q', '').strip().lower()
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    no_results = query and not products.exists()

    return render(request, 'main/product_list.html', {
        'products': products,
        'search_query': request.GET.get('q', ''),
        'no_results': no_results,
    })

def about(request):
    return render(request, 'main/about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Send email to site admin
            send_mail(
                f'New contact form submission: {subject}',
                f'From: {name} <{email}>\n\n{message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )

            # Send confirmation email to user
            send_mail(
                'Thank you for contacting us',
                f'Hi {name},\n\nThank you for your message. We will get back to you shortly.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            messages.success(request, "Thank you for your message! We'll get back to you soon.")
            form = ContactForm()  # Clear the form after success
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()

    return render(request, 'main/contact.html', {'form': form})

# --- Cart Views ---

def add_to_cart(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Product, id=product_id)

        cart = request.session.get("cart", {})
        product_id_str = str(product_id)

        if product_id_str in cart:
            cart[product_id_str]['quantity'] += 1
        else:
            cart[product_id_str] = {
                "name": product.name,
                "image_url": product.image_url,
                "quantity": 1,
            }

        request.session["cart"] = cart
        messages.success(request, f'"{product.name}" added to your cart.')
        return redirect("product_list")

    return redirect("product_list")

def cart_view(request):
    cart = request.session.get('cart', {})
    return render(request, 'main/cart.html', {'cart': cart})

def cart_increase(request, item_id):
    cart = request.session.get('cart', {})
    item_id = str(item_id)
    if item_id in cart:
        cart[item_id]['quantity'] += 1
        request.session['cart'] = cart
        messages.success(request, f"Increased quantity of {cart[item_id]['name']}.")
    return redirect('cart')

def cart_decrease(request, item_id):
    cart = request.session.get('cart', {})
    item_id = str(item_id)
    if item_id in cart:
        if cart[item_id]['quantity'] > 1:
            cart[item_id]['quantity'] -= 1
            messages.success(request, f"Decreased quantity of {cart[item_id]['name']}.")
        else:
            name = cart[item_id]['name']
            del cart[item_id]
            messages.success(request, f"Removed {name} from cart.")
        request.session['cart'] = cart
    return redirect('cart')

def cart_delete(request, item_id):
    cart = request.session.get('cart', {})
    item_id = str(item_id)
    if item_id in cart:
        name = cart[item_id]['name']
        del cart[item_id]
        request.session['cart'] = cart
        messages.success(request, f"Removed {name} from cart.")
    return redirect('cart')

# User account page - login required
@login_required  # <-- decorator added here
def account(request):
    return render(request, 'main/account.html')

# User signup view for registration
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in user immediately
            messages.success(request, "Registration successful. Welcome!")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
