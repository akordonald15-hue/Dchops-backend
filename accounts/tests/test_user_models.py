import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_create_user():
    u = User.objects.create_user(username="donald", password="p")
    assert u.username == "donald"
    assert u.is_active
