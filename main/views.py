from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .forms import ContactForm, RegistrationForm
from .models import Product, Order

from decimal import Decimal
import time
import stripe  # Stripe for payment

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

# --- NEW: Privacy page ---
def privacy(request):
    return render(request, 'main/privacy.html')

# --- NEW: Shipping page ---
def shipping(request):
    return render(request, 'main/shipping.html')

# --- NEW: Terms & Conditions page ---
def terms(request):
    return render(request, 'main/terms.html')

# --- NEW: Coupons & Promotions page ---
def coupons(request):
    COUPONS = {
        "CANDY10": {"type": "percent", "value": 10, "label": "10% off"},
        "SAVE5": {"type": "amount", "value": 5.00, "label": "$5 off"},
        "FREESHIP": {"type": "freeship", "value": 0, "label": "Free shipping"},
    }

    if request.method == "POST":
        code = (request.POST.get("code") or "").strip().upper()
        promo = COUPONS.get(code)
        if not code:
            messages.error(request, "Please enter a code.")
            return redirect("coupons")
        if not promo:
            messages.error(request, f"Code '{code}' is invalid or expired.")
            return redirect("coupons")

        request.session["promo"] = {"code": code, **promo}
        request.session.modified = True
        messages.success(request, f"Applied: {promo['label']} (code {code}).")
        return redirect("cart")

    current = request.session.get("promo")
    return render(request, "main/coupons.html", {"current_promo": current})

# --- NEW: Reviews page ---
def reviews(request):
    return render(request, 'main/reviews.html')

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
    return render(request, 'main/cart.html', {
        'cart': cart,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,  # Stripe public key
    })

@require_POST
def create_checkout_session(request):
    """
    Creates a Stripe Checkout session for everything in the cart
    and redirects the browser to Stripe (no JS needed).
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY

    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')

    line_items = []
    currency = "usd"

    for key, item in cart.items():
        # Gift certificates
        if str(key).startswith("gift:") or item.get("type") == "gift_certificate":
            try:
                amt_cents = int(float(item.get("amount", "0")) * 100)
            except Exception:
                amt_cents = 0
            if amt_cents <= 0:
                continue
            line_items.append({
                "price_data": {
                    "currency": currency,
                    "product_data": {"name": item.get("name", "Gift Certificate")},
                    "unit_amount": amt_cents,
                },
                "quantity": 1,
            })
        else:
            # Regular product
            try:
                product = Product.objects.get(id=int(key))
            except (ValueError, Product.DoesNotExist):
                continue

            qty = int(item.get("quantity", 1))
            unit_price = getattr(product, "price", 0)
            try:
                unit_cents = int(float(unit_price) * 100)
            except Exception:
                unit_cents = 0
            if unit_cents <= 0 or qty <= 0:
                continue

            line_items.append({
                "price_data": {
                    "currency": currency,
                    "product_data": {"name": product.name},
                    "unit_amount": unit_cents,
                },
                "quantity": qty,
            })

    if not line_items:
        return redirect('cart')

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=request.build_absolute_uri("/cart/?success=1"),
            cancel_url=request.build_absolute_uri("/cart/?canceled=1"),
        )
    except Exception as e:
        messages.error(request, f"Payment error: {e}")
        return redirect('cart')

    # Redirect the user to Stripe Checkout
    return redirect(session.url, code=303)

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

# --- Gift Certificates Page ---
def gift_certificates(request):
    TEST_CODES = {
        "12345": {"balance": "50.00", "expires": "2026-12-31"},
        "00000": {"balance": "0.00",  "expires": "2026-12-31"},
        "777777": {"balance": "25.00", "expires": "2026-06-30"},
    }

    if request.method == 'POST':
        if "code" in request.POST:
            code = (request.POST.get("code") or "").strip()
            if not code.isdigit():
                messages.error(request, "Please enter numbers only.")
                return redirect('gift_certificates')

            info = TEST_CODES.get(code)
            if info:
                messages.success(
                    request,
                    f"✅ Code {code} is valid. Balance: ${info['balance']} — Expires: {info['expires']} (demo)"
                )
            else:
                messages.error(request, f"❌ Code {code} is invalid or not found (demo).")
            return redirect('gift_certificates')

        name = (request.POST.get('name') or '').strip()
        email = (request.POST.get('email') or '').strip()
        amount_str = (request.POST.get('amount') or '').strip()

        if not name or not email or not amount_str:
            messages.error(request, "Please fill out all fields before submitting.")
            return redirect('gift_certificates')

        try:
            amount = Decimal(amount_str)
        except Exception:
            messages.error(request, "Amount must be a valid number.")
            return redirect('gift_certificates')

        if amount < 1:
            messages.error(request, "Minimum amount is $1.")
            return redirect('gift_certificates')

        cart = request.session.get("cart", {})
        gc_key = f"gift:{int(time.time())}"
        cart[gc_key] = {
            "type": "gift_certificate",
            "name": f"Gift Certificate for {name} (${amount})",
            "image_url": "",
            "quantity": 1,
            "amount": str(amount),
            "recipient_email": email,
        }
        request.session["cart"] = cart

        messages.success(request, f"Added gift certificate (${amount}) to your cart.")
        return redirect('cart')

    return render(request, 'main/gift_certificates.html')
