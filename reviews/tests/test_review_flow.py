import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from menu.models import Category, MenuItem
from reviews.models import Review

User = get_user_model()
REVIEWS_URL = "/api/reviews/"


@pytest.fixture
def regular_user():
    return User.objects.create_user(username="user", password="p")


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username="admin", email="admin@test.com", password="p"
    )


@pytest.fixture
def category():
    return Category.objects.create(name="Sides", slug="sides")


@pytest.fixture
def menu_item(category):
    return MenuItem.objects.create(
        category=category,
        name="Fries",
        slug="fries",
        price=500,
        is_available=True
    )


@pytest.fixture
def review(regular_user, menu_item):
    return Review.objects.create(
        user=regular_user,
        menu_item=menu_item,
        rating=4,
        text="Good"
    )


@pytest.mark.django_db
class TestReviews:

    def test_authenticated_user_can_post_review(self, client, regular_user, menu_item):
        client.force_login(regular_user)
        payload = {"menu_item": menu_item.id, "rating": 5, "text": "Excellent!"}
        r = client.post(REVIEWS_URL, data=payload)
        assert r.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)
        assert Review.objects.filter(
            menu_item=menu_item,
            user=regular_user,
            text="Excellent!"
        ).exists()


    def test_public_can_fetch_reviews(self, client, review):
        r = client.get(REVIEWS_URL)
        assert r.status_code == status.HTTP_200_OK
        data = r.json()
        results = data.get("results", data)
        assert any(r["id"] == review.id for r in results)


    def test_admin_can_update_status(self, client, admin_user, review):
        client.force_login(admin_user)
        url = f"{REVIEWS_URL}{review.id}/update_status/"
        payload = {"status": "approved"}
        r = client.patch(url, data=payload)
        assert r.status_code == status.HTTP_200_OK

        review.refresh_from_db()
        assert review.status == "approved"

        json_data = r.json()
        assert json_data["old_status"] == "pending"
        assert json_data["new_status"] == "approved"


    def test_regular_user_cannot_update_status(self, client, regular_user, review):
        client.force_login(regular_user)
        url = f"{REVIEWS_URL}{review.id}/update_status/"
        payload = {"status": "approved"}
        r = client.patch(url, data=payload)
        assert r.status_code == status.HTTP_403_FORBIDDEN

        review.refresh_from_db()
        assert review.status == "pending"
