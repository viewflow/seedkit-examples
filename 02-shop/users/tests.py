import pytest

from users.models import User


@pytest.mark.django_db
def test_create_user_by_email():
    user = User.objects.create_user(email="person@example.com", password="s3cr3t-pass")
    assert user.email == "person@example.com"
    assert user.check_password("s3cr3t-pass")


@pytest.mark.django_db
def test_healthz_smoke(client):
    assert client.get("/healthz").status_code == 200
