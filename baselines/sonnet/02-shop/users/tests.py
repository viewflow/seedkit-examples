import pytest

from users.models import User


@pytest.mark.django_db
class TestUserManager:
    def test_create_user(self):
        user = User.objects.create_user(email="jane@example.com", password="s3cret-pass")
        assert user.email == "jane@example.com"
        assert user.check_password("s3cret-pass")
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_superuser(self):
        user = User.objects.create_superuser(email="admin@example.com", password="s3cret-pass")
        assert user.is_staff
        assert user.is_superuser

    def test_create_user_requires_email(self):
        with pytest.raises(ValueError):
            User.objects.create_user(email="", password="s3cret-pass")

    def test_str(self):
        user = User.objects.create_user(email="jane@example.com", password="s3cret-pass")
        assert str(user) == "jane@example.com"
