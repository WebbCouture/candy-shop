from django.contrib.auth.views import LoginView  # Importing built-in LoginView
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Home, Products, About, Contact pages
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # Cart-related URLs
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),

    # Cart item quantity management URLs
    path('cart/increase/<int:item_id>/', views.cart_increase, name='cart_increase'),
    path('cart/decrease/<int:item_id>/', views.cart_decrease, name='cart_decrease'),
    path('cart/delete/<int:item_id>/', views.cart_delete, name='cart_delete'),

    # Account-related URLs (Login and Registration)
    path('account/login/', LoginView.as_view(), name='login'),  # Login page using Django's built-in view
    # If you have a custom login view, replace the above line with:
    # path('account/login/', views.custom_login, name='login'),

    # Optionally, if you have a registration page:
    # path('account/register/', views.register, name='register'),
]

# Static files handling when DEBUG is False
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
