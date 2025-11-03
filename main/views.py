from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Product, Order, GiftCertificate
from decimal import Decimal, ROUND_HALF_UP
import time
import stripe

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

User = get_user_model()


def to_cents(amount) -> int:
    """Convert Decimal/str/float to integer cents."""
    d = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int((d * 100).to_integral_value())


# === PRODUCT LIST + SEARCH ===
def product_list(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    no_results = bool(query) and not products.exists()
    return render(request, 'main/product_list.html', {
        'products': products,
        'search_query': query,
        'no_results': no_results,
    })


# === STATIC PAGES ===
def reviews(request):
    return render(request, 'main/reviews.html')

def blog(request):
    return render(request, 'main/blog.html')

def recipes(request):
    return render(request, 'main/recipes.html')

def shipping(request):
    return render(request, 'main/shipping.html')


# === CART VIEWS ===
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
    # Handle Stripe return
    if request.GET.get('success') == '1':
        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True
        messages.success(request, "Payment successful! Your order is confirmed.")
        return redirect('cart')

    if request.GET.get('canceled') == '1':
        messages.warning(request, "Payment canceled. Your items are still in the cart.")
        return redirect('cart')

    cart = request.session.get('cart', {})
    public_key = getattr(settings, 'STRIPE_PUBLIC_KEY', '')
    items = []
    subtotal = Decimal('0.00')
    currency = getattr(settings, 'STRIPE_CURRENCY', 'usd').upper()

    for key, item in cart.items():
        if str(key).startswith("gift:") or item.get("type") == "gift_certificate":
            qty = int(item.get("quantity", 1))
            try:
                unit_price = Decimal(item.get("amount", "0"))
            except Exception:
                unit_price = Decimal('0.00')
            line_total = unit_price * qty
            items.append({
                "id": key,
                "name": item.get("name", "Gift Certificate"),
                "description": "",
                "quantity": qty,
                "unit_price": unit_price,
                "line_total": line_total,
                "is_gift": True,
            })
            subtotal += line_total
        else:
            try:
                product = Product.objects.get(id=int(key))
            except (ValueError, Product.DoesNotExist):
                continue
            qty = int(item.get("quantity", 1))
            unit_price = Decimal(product.price or 0)
            line_total = unit_price * qty
            items.append({
                "id": key,
                "name": product.name,
                "description": getattr(product, "description", ""),
                "quantity": qty,
                "unit_price": unit_price,
                "line_total": line_total,
                "is_gift": False,
            })
            subtotal += line_total

    total = subtotal.quantize(Decimal('0.01'))

    return render(request, 'main/cart.html', {
        'cart': cart,
        'STRIPE_PUBLIC_KEY': public_key,
        "items": items,
        "has_items": bool(items),
        "subtotal": subtotal,
        "total": total,
        "currency": currency,
    })


@require_POST
def create_checkout_session(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')

    line_items = []
    currency = getattr(settings, "STRIPE_CURRENCY", "usd")

    for key, item in cart.items():
        if str(key).startswith("gift:") or item.get("type") == "gift_certificate":
            try:
                amt_cents = to_cents(item.get("amount", "0"))
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
            try:
                product = Product.objects.get(id=int(key))
            except (ValueError, Product.DoesNotExist):
                continue
            qty = int(item.get("quantity", 1))
            try:
                unit_cents = to_cents(product.price)
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
            mode="payment",
            line_items=line_items,
            success_url=request.build_absolute_uri("/cart/?success=1"),
            cancel_url=request.build_absolute_uri("/cart/?canceled=1"),
        )
    except Exception as e:
        messages.error(request, f"Payment error: {e}")
        return redirect('cart')

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


# === ACCOUNT + LOGIN/SIGNUP ===
def account(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user).order_by('-date')
        return render(request, "main/account.html", {
            "dashboard": True,
            "orders": orders
        })

    login_form = AuthenticationForm()
    signup_form = UserCreationForm()

    if request.method == "POST":
        if "login" in request.POST:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                messages.success(request, "Inloggad!")
                return redirect("account")
        elif "signup" in request.POST:
            signup_form = UserCreationForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)
                messages.success(request, "Konto skapat!")
                return redirect("account")

    return render(request, "main/account.html", {
        "login_form": login_form,
        "signup_form": signup_form
    })


def logout_view(request):
    logout(request)
    messages.success(request, "Du har loggats ut.")
    return redirect('account')


# === GIFT CERTIFICATES ===
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
                    f"Code {code} is valid. Balance: ${info['balance']} — Expires: {info['expires']} (demo)"
                )
            else:
                messages.error(request, f"Code {code} is invalid or not found (demo).")
            return redirect('gift_certificates')

        name = (request.POST.get('name') or '').strip()
        email = (request.POST.get('email') or '').strip()
        amount_str = (request.POST.get('amount') or '').strip()

        if not name or not email or not amount_str:
            messages.error(request, "Please fill out all fields.")
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

        GiftCertificate.objects.create(
            recipient_name=name,
            recipient_email=email,
            amount=amount,
            message="",
            status="pending",
        )

        messages.success(request, f"Added gift certificate (${amount}) to your cart.")
        return redirect('cart')

    return render(request, 'main/gift_certificates.html')


# === PURCHASE HISTORY ===
@login_required
def purchase_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    discount = 10  # Example discount
    return render(request, 'main/purchase_history.html', {
        'orders': orders,
        'discount': discount,
    })


# ==================== LOGIN + SIGNUP (SEPARATA SIDOR) ====================

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Inloggad!")
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Konto skapat!")
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'main/signup.html', {'form': form})