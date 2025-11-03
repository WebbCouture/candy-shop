from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # === HEMSIDA + PRODUKTER ===
    path('products/', views.product_list, name='product_list'),
    path('shipping/', views.shipping, name='shipping'),
    path('reviews/', views.reviews, name='reviews'),
    path('blog/', views.blog, name='blog'),
    path('recipes/', views.recipes, name='recipes'),

    # === KUNDVAGN ===
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),

    # === KUNDVAGN – ÄNDRA ANTAL ===
    path('cart/increase/<path:item_id>/', views.cart_increase, name='cart_increase'),
    path('cart/decrease/<path:item_id>/', views.cart_decrease, name='cart_decrease'),
    path('cart/delete/<path:item_id>/', views.cart_delete, name='cart_delete'),

    # === KONTO ===
    path('account/', views.account, name='account'),
    path('login/', views.login_view, name='login'),        # NYTT
    path('signup/', views.signup_view, name='signup'),    # NYTT
    path('logout/', views.logout_view, name='logout'),

    # === GÅVOBEVIS ===
    path('gift-certificates/', views.gift_certificates, name='gift_certificates'),

    # === KÖPHISTORIK ===
    path('account/purchase-history/', views.purchase_history, name='purchase_history'),
]

# === STATISKA FILER (endast i produktion) ===
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)