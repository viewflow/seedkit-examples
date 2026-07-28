import pytest
from django.contrib.auth.models import User
from django.test import Client


@pytest.mark.django_db
def test_export_requires_login(client: Client) -> None:
    response = client.get("/privacy/export/")
    assert response.status_code == 302


@pytest.mark.django_db
def test_export_returns_user_data(client: Client) -> None:
    user = User.objects.create_user("alice", "alice@example.com")
    client.force_login(user)
    data = client.get("/privacy/export/").json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"


@pytest.mark.django_db
def test_delete_account_erases_user(client: Client) -> None:
    user = User.objects.create_user("bob", "bob@example.com")
    client.force_login(user)
    response = client.post("/privacy/delete/")
    assert response.status_code == 302
    assert not User.objects.filter(pk=user.pk).exists()
