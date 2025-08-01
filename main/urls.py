from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),  # Added for cart functionality
    path('cart/', views.cart_view, name='cart'),  # New cart page route
]
