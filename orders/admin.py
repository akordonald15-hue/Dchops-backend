from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('menu_item', 'price', 'quantity')
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'paid', 'created_at')
    list_filter = ('status', 'paid')
    search_fields = ('id', 'user__username')
    readonly_fields = ('total', 'created_at', 'updated_at', 'paystack_reference', 'paid')
    list_editable = ('status',)
    inlines = [OrderItemInline]
