"""Custom user model and allauth wiring."""

import pytest
from django.core import mail

from users.models import User


@pytest.mark.django_db
def test_user_is_created_with_email_as_identifier():
    user = User.objects.create_user(email="a@example.com", password="pw")

    assert user.get_username() == "a@example.com"
    assert User.USERNAME_FIELD == "email"
    assert not hasattr(user, "username") or user.username is None


@pytest.mark.django_db
def test_superuser_gets_staff_flags():
    user = User.objects.create_superuser(email="root@example.com", password="pw")
    assert user.is_staff and user.is_superuser


@pytest.mark.django_db
def test_signup_sends_a_verification_email(client):
    response = client.post(
        "/accounts/signup/",
        {
            "email": "new@example.com",
            "password1": "a-long-enough-passphrase",
            "password2": "a-long-enough-passphrase",
        },
    )

    assert response.status_code == 302
    assert User.objects.filter(email="new@example.com").exists()
    assert len(mail.outbox) == 1
    assert "confirm" in mail.outbox[0].body.lower()


@pytest.mark.django_db
def test_unverified_user_cannot_log_in(client, user):
    response = client.post(
        "/accounts/login/",
        {"login": user.email, "password": "s3cret-passphrase"},
        follow=True,
    )
    # Mandatory verification: allauth redirects to the "verify your e-mail" page.
    assert response.status_code == 200
    assert b"confirm" in response.content.lower() or b"verif" in response.content.lower()
