import pytest

from users.models import User


@pytest.mark.django_db
def test_create_user_with_email():
    user = User.objects.create_user(
        username="jane", email="jane@example.com", password="s3cr3t-pass"
    )

    assert user.email == "jane@example.com"
    assert user.check_password("s3cr3t-pass")


@pytest.mark.django_db
def test_str_returns_email():
    user = User.objects.create_user(
        username="jane", email="jane@example.com", password="s3cr3t-pass"
    )

    assert str(user) == "jane@example.com"
