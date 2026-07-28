import pytest
from django.contrib.auth import get_user_model

from users.models import User


def test_custom_user_model_is_active():
    assert get_user_model() is User


@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(username="alice", email="alice@example.com", password="x")
    assert user.pk is not None
    assert not user.is_staff


@pytest.mark.django_db
def test_accounts_login_page(client):
    response = client.get("/accounts/login/")
    assert response.status_code == 200
