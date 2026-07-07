import pytest

from users.models import User

pytestmark = pytest.mark.django_db


def test_create_user():
    user = User.objects.create_user(email="jane@example.com", password="s3cr3t-pass")

    assert user.email == "jane@example.com"
    assert user.check_password("s3cr3t-pass")
    assert not user.is_staff
    assert not user.is_superuser


def test_create_superuser():
    user = User.objects.create_superuser(email="admin@example.com", password="s3cr3t-pass")

    assert user.is_staff
    assert user.is_superuser
