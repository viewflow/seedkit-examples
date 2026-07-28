"""Admin reachability and django-axes lockout behaviour."""

import pytest
from django.test import override_settings


def test_admin_login_page_is_reachable(client, db):
    response = client.get("/admin/login/")
    assert response.status_code == 200


@pytest.mark.django_db
@override_settings(AXES_FAILURE_LIMIT=3)
def test_axes_locks_out_after_repeated_failures(client, user):
    for _ in range(3):
        client.post("/accounts/login/", {"login": user.email, "password": "wrong"})

    response = client.post(
        "/accounts/login/", {"login": user.email, "password": "s3cret-passphrase"}
    )
    # Axes answers a locked-out attempt with 429 and its lockout template.
    assert response.status_code == 429
    assert b"Too many sign-in attempts" in response.content
