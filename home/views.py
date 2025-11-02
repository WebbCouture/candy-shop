from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

from .forms import ContactForm
from .models import TeamMember, Message  # ← Rätt: finns i home.models
from main.models import Product, Cart, CartItem, Order, OrderItem  # ← Rätt: finns i main.models


# Home page - shows latest products
def home(request):
    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())
    latest_products = Product.objects.all().order_by('-id')[:3]
    return render(request, 'home/home.html', {
        'cart_count': cart_count,
        'latest_products': latest_products,
    })


# About page
def about(request):
    team = TeamMember.objects.all()
    return render(request, 'home/about.html', {"team": team})


def team(request):
    team_members = TeamMember.objects.all()
    return render(request, 'home/team.html', {'team_members': team_members})


# Contact form
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save to DB (Message model) manually
            msg_obj = Message.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
            )

            # Send notification to admin
            send_mail(
                f'New contact form submission: {msg_obj.subject}',
                f'From: {msg_obj.name} <{msg_obj.email}>\n\n{msg_obj.message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )

            # Send confirmation to the user
            send_mail(
                'Thank you for contacting us',
                f'Hi {msg_obj.name},\n\nThank you for your message. We will get back to you shortly.',
                settings.DEFAULT_FROM_EMAIL,
                [msg_obj.email],
                fail_silently=False,
            )

            messages.success(request, "Thank you for your message! We'll get back to you soon.")
            return redirect('contact')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()

    return render(request, 'home/contact.html', {'form': form})


# --- Static pages ---
def privacy(request):
    return render(request, 'home/privacy.html')


def terms(request):
    return render(request, 'home/terms.html')


# --- CART & CHECKOUT VIEWS (flyttade från main/views.py) ---
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from decimal import Decimal
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def cart(request):
    cart_obj, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart_obj.items.all()
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'main/cart.html', {
        'cart_items': cart_items,
        'total': total
    })


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_obj, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart_obj,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{product.name} added to cart!")
    return redirect('cart')


@login_required
def update_cart(request, item_id):
    if request.method == "POST":
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
        return redirect('cart')
    return redirect('cart')


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart')


@login_required
def checkout(request):
    cart_obj = get_object_or_404(Cart, user=request.user)
    cart_items = cart_obj.items.all()
    total = sum(item.total_price() for item in cart_items)

    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    if request.method == "POST":
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(total * 100),
                currency='usd',
                metadata={'user_id': request.user.id}
            )
            return render(request, 'main/checkout.html', {
                'cart_items': cart_items,
                'total': total,
                'client_secret': intent.client_secret,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY
            })
        except Exception as e:
            messages.error(request, f"Payment error: {str(e)}")
            return redirect('cart')

    return render(request, 'main/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })


@login_required
def stripe_success(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()

        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('cart')

        total = sum(item.total_price() for item in cart_items)

        # SKAPA ORDER
        order = Order.objects.create(
            user=request.user,
            total=total,
            status='paid'
        )

        # SKAPA ORDERITEMS
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # TÖM KUNDVAGN
        cart_items.delete()

        messages.success(request, "Payment successful! Your order is confirmed.")
        return render(request, 'main/success.html', {'order': order})

    except Exception as e:
        messages.error(request, f"Order error: {str(e)}")
        return redirect('cart')


@login_required
def stripe_cancel(request):
    messages.error(request, "Payment cancelled.")
    return redirect('cart')