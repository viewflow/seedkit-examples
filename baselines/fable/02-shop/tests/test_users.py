import pytest
from django.contrib.auth import get_user_model

from users.models import User


@pytest.mark.django_db
def test_create_user() -> None:
    user = User.objects.create_user(
        username="alice",
        email="alice@example.com",
        password="a-strong-password-123",
    )
    assert user.pk is not None
    assert user.check_password("a-strong-password-123")


def test_custom_user_model_is_active() -> None:
    assert get_user_model() is User
