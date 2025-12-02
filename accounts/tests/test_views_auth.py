import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models import EmailVerification

User = get_user_model()

REGISTER_URL = "/api/accounts/register/"
LOGIN_URL = "/api/accounts/login/"


@pytest.mark.django_db
def test_register_and_login(client):
    # Step 1: Register user
    payload = {
        "username": "donald",
        "email": "donald@example.com",
        "password": "StrongPass123",
        "password2": "StrongPass123"
    }
    r = client.post(REGISTER_URL, data=payload)
    assert r.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)
    body = r.json()
    assert body.get("success", True) is True

    # Step 2: ✅ VERIFY EMAIL (required before login)
    user = User.objects.get(username="donald")
    verification = EmailVerification.objects.get(user=user)
    verification.is_verified = True
    verification.save()

    # Step 3: Login should now work
    login_payload = {"username": "donald", "password": "StrongPass123"}
    r2 = client.post(LOGIN_URL, data=login_payload)
    assert r2.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
    
    # ✅ FIXED: Check for tokens instead of "success" field
    response_data = r2.json()
    assert response_data.get("access") is not None  # Has access token
    assert response_data.get("refresh") is not None  # Has refresh token
    assert response_data.get("user") is not None  # Has user info
    assert response_data["user"]["username"] == "donald"