import pytest
from django.contrib.auth.models import User

from core.gdpr import delete_user_data, export_user_data, scrub_sentry_event


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="alice",
        email="alice@example.com",
        password="s3cret",
        first_name="Alice",
    )


def test_export_user_data(user):
    data = export_user_data(user)
    assert data["user"]["username"] == "alice"
    assert data["user"]["email"] == "alice@example.com"


def test_delete_user_data_anonymises(user):
    delete_user_data(user)
    user.refresh_from_db()
    assert user.username == f"deleted-user-{user.pk}"
    assert user.email == ""
    assert user.first_name == ""
    assert not user.is_active
    assert not user.has_usable_password()


def test_scrub_sentry_event_strips_pii():
    event = {
        "request": {
            "cookies": {"sessionid": "abc"},
            "headers": {"Authorization": "Bearer xyz", "Accept": "text/html"},
            "data": {"password": "hunter2", "comment": "hi"},
            "env": {},
        },
        "user": {"id": 42, "email": "alice@example.com", "ip_address": "10.0.0.1"},
        "extra": {"token": "abc123", "safe": "value"},
    }

    scrubbed = scrub_sentry_event(event, {})

    assert "cookies" not in scrubbed["request"]
    assert scrubbed["request"]["headers"]["Authorization"] == "[Scrubbed]"
    assert scrubbed["request"]["headers"]["Accept"] == "text/html"
    assert scrubbed["request"]["data"]["password"] == "[Scrubbed]"
    assert scrubbed["request"]["data"]["comment"] == "hi"
    assert scrubbed["user"] == {"id": 42}
    assert scrubbed["extra"]["token"] == "[Scrubbed]"
    assert scrubbed["extra"]["safe"] == "value"
