from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from django.contrib import messages  # For the messages framework

def home(request):
    cart = request.session.get('cart', [])
    cart_count = len(cart)
    return render(request, 'main/home.html', {'cart_count': cart_count})

def product_list(request):
    products = [
        {
            'name': 'Cherry Delight',
            'description': 'Sweet cherry flavored candy, perfect for any occasion.',
            'image_url': 'https://images.unsplash.com/photo-1603202902092-3eb7a76ecf5f?q=80&w=687&auto=format&fit=crop',
        },
        {
            'name': 'Chocolate Bliss',
            'description': 'Rich chocolate candy made with premium cocoa.',
            'image_url': 'https://images.unsplash.com/photo-1534119139482-b530a7f9a98b?q=80&w=735&auto=format&fit=crop',
        },
        {
            'name': 'Fruit Punch',
            'description': 'Refreshing fruity candy bursting with flavor.',
            'image_url': 'https://images.unsplash.com/photo-1600359746315-119f1360d663?q=80&w=688&auto=format&fit=crop',
        },
    ]

    query = request.GET.get('q', '').strip().lower()
    if query:
        filtered_products = [product for product in products if query in product['name'].lower()]
    else:
        filtered_products = products

    no_results = query and not filtered_products

    context = {
        'products': filtered_products,
        'search_query': request.GET.get('q', ''),
        'no_results': no_results,
    }

    return render(request, 'main/product_list.html', context)

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

            # Send email to site owner
            send_mail(
                f'New contact form submission: {subject}',
                f'From: {name} <{email}>\n\n{message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,  # So errors are raised during development
            )

            # Confirmation email to user
            send_mail(
                'Thank you for contacting us',
                f'Hi {name},\n\nThank you for your message. We will get back to you shortly.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            messages.success(request, "Thank you for your message! We'll get back to you soon.")
            form = ContactForm()  # Reset the form after successful submission
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()

    return render(request, 'main/contact.html', {'form': form})

# --- New add to cart view ---
def add_to_cart(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name")
        product_image = request.POST.get("product_image")

        if not product_name:
            messages.error(request, "Invalid product.")
            return redirect("product_list")

        # Initialize cart in session if not exists
        cart = request.session.get("cart", [])

        # Add product to cart as dict
        cart.append({
            "name": product_name,
            "image_url": product_image,
        })

        # Save back to session
        request.session["cart"] = cart

        messages.success(request, f'"{product_name}" added to your cart.')
        return redirect("product_list")

    # If GET or other method, redirect to products
    return redirect("product_list")

# --- New cart view ---
def cart_view(request):
    cart = request.session.get('cart', [])
    context = {
        'cart': cart,
    }
    return render(request, 'main/cart.html', context)
