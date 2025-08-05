from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # Cart related URLs
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),

    # Cart item quantity management URLs
    path('cart/increase/<int:item_id>/', views.cart_increase, name='cart_increase'),
    path('cart/decrease/<int:item_id>/', views.cart_decrease, name='cart_decrease'),
    path('cart/delete/<int:item_id>/', views.cart_delete, name='cart_delete'),

    # Account page URL
    path('account/', views.account, name='account'),

    # Signup page URL
    path('signup/', views.signup, name='signup'),
]
