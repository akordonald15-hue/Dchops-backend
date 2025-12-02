from django.contrib import admin
from .models import Order, OrderItem

# Inline for OrderItem
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["menu_item", "quantity", "price", "line_total"]
    can_delete = False
    fields = ["menu_item", "quantity", "price", "line_total"]

    def line_total(self, obj):
        return obj.line_total()
    line_total.short_description = "Line Total"

# Order admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'get_total', 'paid', 'created_at')
    list_filter = ('status', 'paid')
    search_fields = ('id', 'user__username')
    readonly_fields = ('get_total', 'created_at', 'updated_at', 'paystack_reference', 'paid')
    list_editable = ('status',)
    inlines = [OrderItemInline]

    # Use a callable for total
    def get_total(self, obj):
        return obj.total
    get_total.short_description = 'Total'
