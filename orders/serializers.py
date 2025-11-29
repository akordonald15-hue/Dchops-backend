# orders/serializers.py
from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .models import Order, OrderItem
from menu.models import MenuItem
from menu.serializers import MenuItemSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_detail = MenuItemSerializer(source='menu_item', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_detail', 'quantity', 'price']
        read_only_fields = ['id', 'menu_item_detail', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = serializers.ReadOnlyField(source='user.username')
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'status', 'total', 'address', 'phone',
            'created_at', 'items', 'paid', 'paystack_reference'
        ]
        read_only_fields = ['id', 'total', 'created_at', 'paid', 'paystack_reference']

    # FIELD VALIDATION ------------------------------

    def validate_address(self, value):
        value = value.strip()
        if len(value) < 5:
            raise serializers.ValidationError("Address is too short.")
        return value

    def validate_phone(self, value):
        value = value.strip()
        if not value.isdigit() or len(value) < 8:
            raise serializers.ValidationError("Invalid phone number.")
        return value

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must contain at least one item.")
        return value

    # CREATE ORDER ----------------------------------

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user

        # Create order header
        order = Order.objects.create(user=user, **validated_data)

        total = Decimal('0.00')

        for item_data in items_data:
            menu_item = item_data['menu_item']

            # Validate availability
            if not menu_item.is_available:
                raise serializers.ValidationError(
                    f"Item '{menu_item.name}' is not available."
                )

            quantity = int(item_data.get('quantity', 1))
            if quantity <= 0:
                raise serializers.ValidationError(
                    f"Invalid quantity for '{menu_item.name}'."
                )

            # Create order item
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                price=menu_item.price
            )

            # Update total
            total += menu_item.price * quantity

        # Save total
        order.total = total
        order.save()

        return order

    # UPDATE ORDER -----------------------------------
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
