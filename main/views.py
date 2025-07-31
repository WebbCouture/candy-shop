from django.shortcuts import render
from .models import Product  # Only needed if you have a Product model

def home(request):
    return render(request, 'main/home.html')

def product_list(request):
    # If you don't have a Product model yet, just pass a dummy list for now
    # Example: products = [{'name': 'Candy A', 'price': 2.99}, ...]
    return render(request, 'main/product_list.html')

def about(request):
    return render(request, 'main/about.html')

def contact(request):
    return render(request, 'main/contact.html')
