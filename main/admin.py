from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Product, Cart, CartItem, 
    Order, OrderItem, GiftCertificate, TeamMember
)

# --- Product ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'image_url']
    search_fields = ['name']

# --- GiftCertificate ---
@admin.register(GiftCertificate)
class GiftCertificateAdmin(admin.ModelAdmin):
    list_display = ("code", "recipient_name", "amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("code", "recipient_name", "recipient_email")
    readonly_fields = ("code", "created_at")

# --- Cart ---
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "updated_at")
    search_fields = ("user__username",)
    readonly_fields = ("created_at", "updated_at")

# --- CartItem ---
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "total_price")
    search_fields = ("cart__user__username", "product__name")
    readonly_fields = ("cart", "product", "quantity", "total_price")

# --- Order ---
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'total', 'date']
    list_filter = ['date']
    search_fields = ['user__username']

# --- OrderItem ---
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    search_fields = ['order__user__username', 'product__name']

# --- TeamMember ---
@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'photo_tag')
    search_fields = ('name', 'role')
    
    def photo_tag(self, obj):
        if obj.photo_url:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:5px;" />',
                obj.photo_url
            )
        return "-"
    photo_tag.short_description = 'Photo'
