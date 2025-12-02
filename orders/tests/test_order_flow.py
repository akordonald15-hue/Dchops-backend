import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from menu.models import Category, MenuItem
from orders.models import Order

User = get_user_model()
ORDER_CREATE_URL = "/api/orders/"  # Correct URL from router


@pytest.mark.django_db
def test_order_create_flow(client):
    # Create user
    user = User.objects.create_user(username="c", password="p")
    client.force_login(user)

    # Create category and menu item
    category = Category.objects.create(name="Wraps", slug="wraps")
    menu_item = MenuItem.objects.create(
        category=category,
        name="Chicken Wrap",
        slug="chicken-wrap",
        description="Tasty",
        price=1200,
        is_available=True
    )

    # Payload with correct keys
    payload = {"items": [{"menu_item": menu_item.id, "quantity": 1, "price": menu_item.price}]}

    # Post request
    r = client.post(ORDER_CREATE_URL, payload, content_type="application/json")

    assert r.status_code == status.HTTP_201_CREATED

    # Verify order exists in DB
    order = Order.objects.filter(user=user).first()
    assert order is not None
    assert order.items.count() == 1
    assert order.items.first().menu_item == menu_item
    assert order.items.first().quantity == 1
