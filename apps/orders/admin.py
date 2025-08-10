from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem, Delivery, Rider

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'order_time')
    list_filter = ('status', 'order_time')
    search_fields = ('user__username', 'id')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'quantity', 'unit_price', 'total_price')
    search_fields = ('order__id',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'quantity')
    search_fields = ('cart__user__username',)

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'restaurant', 'rider', 'status', 'assigned_at', 'estimated_arrival_time', 'actual_arrival_time')
    list_filter = ('status', 'assigned_at', 'restaurant')
    search_fields = ('order__id__exact', 'restaurant__name', 'rider__name') # Use __exact for exact ID search

@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    

