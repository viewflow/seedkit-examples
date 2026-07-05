import pytest


@pytest.mark.django_db
def test_checkout_requires_login(client):
    response = client.post("/billing/checkout/", {"price_id": "price_123"})
    assert response.status_code == 302
    assert "/accounts/login/" in response.url
