from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  # Import auth views for login, logout, password reset

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

    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
    
    # Password reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]
