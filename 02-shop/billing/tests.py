import pytest


@pytest.mark.django_db
def test_checkout_requires_login(client):
    response = client.get("/billing/checkout/")
    assert response.status_code in (302, 405)
