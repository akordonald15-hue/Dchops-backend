import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models import EmailVerification

User = get_user_model()

@pytest.mark.django_db
def test_register_and_login(client):
    # 1️⃣ Register user
    register_url = reverse('register')
    payload = {
        "username": "donald",
        "email": "donald@example.com",
        "password": "StrongPass123",
        "password2": "StrongPass123"
    }
    resp = client.post(register_url, data=payload, format='json')
    assert resp.status_code == status.HTTP_201_CREATED

    data = resp.json()
    user_data = data.get("user", data)
    user_id = user_data["id"]

    # 2️⃣ Manually verify email
    user = User.objects.get(id=user_id)
    verification = EmailVerification.objects.get(user=user)
    verification.is_verified = True
    verification.save()

    # 3️⃣ Login
    login_url = reverse("login")
    resp2 = client.post(login_url, {
        "username": "donald",
        "password": "StrongPass123"
    }, format='json')

    assert resp2.status_code == status.HTTP_200_OK
    data2 = resp2.json()
    user_data2 = data2.get("user", data2)

    assert user_data2["username"] == "donald"
    assert user_data2["email"] == "donald@example.com"
