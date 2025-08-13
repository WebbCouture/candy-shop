from django.contrib.auth.views import LoginView  # optional; fine to keep
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView   # ← add this import
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

    # Accounts-related URL (Login + Registration combined page)
    path('accounts/', views.account, name='account'),

    # ✅ Redirect any visit to /accounts/login/ to your combined /accounts/ page
    path('accounts/login/', RedirectView.as_view(pattern_name='account', permanent=False)),
]

# Static files handling when DEBUG is False
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
