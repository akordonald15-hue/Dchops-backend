import pytest
from orders.models import Order, OrderItem
from menu.models import Category, MenuItem
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_order_and_items():
    u = User.objects.create_user(username="u", password="p")
    c = Category.objects.create(name="Pizza", slug="pizza")
    m = MenuItem.objects.create(category=c, name="Margherita", slug="margh", price=2500, is_available=True)
    o = Order.objects.create(user=u, status="pending")
    oi = OrderItem.objects.create(order=o, menu_item=m, quantity=1, price=2500)
    assert o.items.count() == 1
