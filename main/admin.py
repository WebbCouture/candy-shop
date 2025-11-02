from django.contrib import admin
from .models import (
    Product, Category,  # LÄGG TILL DESSA!
    Coupon, Cart, CartItem, 
    Order, OrderItem, GiftCertificate  # LÄGG TILL Order/OrderItem!
)

# PRODUCT & CATEGORY (måste ha för CRUD)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'image']
    list_filter = ['category']
    search_fields = ['name']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
    image_preview.short_description = 'Preview'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

# GIFT CERTIFICATE (du har redan – behåll!)
@admin.register(GiftCertificate)
class GiftCertificateAdmin(admin.ModelAdmin):
    list_display = ("code", "recipient_name", "amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("code", "recipient_name", "recipient_email")
    readonly_fields = ("code", "created_at")

# COUPON (du har redan – behåll!)
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "type", "value", "label", "active", "starts_at", "ends_at", "used_count")
    list_filter = ("active", "type", "starts_at", "ends_at")
    search_fields = ("code", "label")
    readonly_fields = ("used_count",)

# CART (du har redan – behåll!)
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "updated_at")
    search_fields = ("user__username",)
    readonly_fields = ("created_at", "updated_at")

# CART ITEM (du har redan – behåll!)
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "total_price")
    search_fields = ("cart__user__username", "product__name")
    readonly_fields = ("cart", "product", "quantity", "total_price")

# ORDER & ORDERITEM (NYTT – ASSESSORN SAKNAR!)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    search_fields = ['order__user__username', 'product__name']