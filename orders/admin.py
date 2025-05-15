from django.contrib import admin
from .models import Order, OrderProduct, Payment

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'order_total', 'status', 'is_ordered', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'user__email', 'user__first_name', 'user__last_name']
    list_per_page = 20
    inlines = [OrderProductInline]

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'user', 'payment_method', 'amount_paid', 'status', 'created_at']
    list_filter = ['status', 'payment_method']
    search_fields = ['payment_id', 'user__email']

admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(OrderProduct)
