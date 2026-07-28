"""The custom 403/404/500 templates only render when DEBUG is off."""

import pytest
from django.test import override_settings
from django.views.defaults import page_not_found, permission_denied, server_error


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_404_uses_the_custom_template(rf):
    response = page_not_found(rf.get("/missing/"), Exception("gone"))
    assert response.status_code == 404
    assert b"We couldn't find that page" in response.content


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_403_uses_the_custom_template(rf):
    response = permission_denied(rf.get("/secret/"), Exception("nope"))
    assert response.status_code == 403
    assert b"You don't have access to this" in response.content


@override_settings(DEBUG=False)
def test_500_uses_the_custom_template(rf):
    response = server_error(rf.get("/boom/"))
    assert response.status_code == 500
    assert b"Something went wrong" in response.content
