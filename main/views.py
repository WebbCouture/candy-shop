from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm

from .forms import ContactForm, RegistrationForm
from .models import Product, Order


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
    query = request.GET.get('q', '').strip()
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    no_results = bool(query) and not products.exists()

    return render(request, 'main/product_list.html', {
        'products': products,
        'search_query': query,
        'no_results': no_results,
    })


# About page
def about(request):
    return render(request, 'main/about.html')


# Contact form
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Send notification to admin
            send_mail(
                f'New contact form submission: {subject}',
                f'From: {name} <{email}>\n\n{message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )

            # Send confirmation to the user
            send_mail(
                'Thank you for contacting us',
                f'Hi {name},\n\nThank you for your message. We will get back to you shortly.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            messages.success(request, "Thank you for your message! We'll get back to you soon.")
            return redirect('contact')
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


# --- Custom Logout View ---
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('account')


# --- Account View (Login, Register, Dashboard) ---
def account(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
        return render(request, 'registration/account.html', {
            'dashboard': True,
            'orders': orders
        })

    login_form = AuthenticationForm()
    signup_form = RegistrationForm()

    if request.method == 'POST':
        if 'login' in request.POST:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('account')
            else:
                messages.error(request, "Invalid credentials, please try again.")

        elif 'signup' in request.POST:
            signup_form = RegistrationForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)
                messages.success(request, "Registration successful! You are now logged in.")
                return redirect('account')
            else:
                messages.error(request, "There were errors in the registration form.")

    return render(request, 'registration/account.html', {
        'login_form': login_form,
        'signup_form': signup_form,
        'dashboard': False
    })
