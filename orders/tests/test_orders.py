import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from menu.models import Category, MenuItem
from orders.models import Order, OrderItem

User = get_user_model()
ORDER_URL = "/api/orders/"  # ✅ FIXED: Removed duplicate "orders"


@pytest.mark.django_db
class TestOrderEndpoints:
    @pytest.fixture
    def user(self):
        return User.objects.create_user(username="user", password="p")

    @pytest.fixture
    def admin(self):
        return User.objects.create_superuser(username="admin", password="p", email="admin@test.com")

    @pytest.fixture
    def category(self):
        return Category.objects.create(name="Wraps", slug="wraps")

    @pytest.fixture
    def menu_item(self, category):
        return MenuItem.objects.create(
            category=category,
            name="Chicken Wrap",
            slug="chicken-wrap",
            description="Tasty",
            price=1200,
            is_available=True
        )

    def test_user_can_create_order(self, client, user, menu_item):
        client.force_login(user)
        payload = {"items": [{"menu_item": menu_item.id, "quantity": 2}]}
        resp = client.post(ORDER_URL, payload, content_type="application/json")
        assert resp.status_code == status.HTTP_201_CREATED
        order = Order.objects.filter(user=user).first()
        assert order is not None
        assert order.items.count() == 1
        assert order.items.first().quantity == 2

    def test_admin_can_update_order_status(self, client, admin, user, menu_item):
        client.force_login(admin)
        order = Order.objects.create(user=user, total_price=1200)  # ✅ FIXED: total -> total_price
        OrderItem.objects.create(order=order, menu_item=menu_item, quantity=1, price=menu_item.price)
        url = f"{ORDER_URL}{order.id}/update_status/"
        resp = client.patch(url, {"status": "DELIVERED"}, content_type="application/json")
        assert resp.status_code == status.HTTP_200_OK
        order.refresh_from_db()
        assert order.status == "DELIVERED"

    def test_user_cannot_update_order_status(self, client, user, menu_item):
        client.force_login(user)
        order = Order.objects.create(user=user, total_price=1200)  # ✅ FIXED: total -> total_price
        OrderItem.objects.create(order=order, menu_item=menu_item, quantity=1, price=menu_item.price)
        url = f"{ORDER_URL}{order.id}/update_status/"
        resp = client.patch(url, {"status": "DELIVERED"}, content_type="application/json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        order.refresh_from_db()
        assert order.status == "PENDING"