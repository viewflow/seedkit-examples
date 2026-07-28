"""Catalogue views and the Stripe checkout seam."""

from decimal import Decimal
from unittest import mock

import pytest
from django.urls import reverse

from shop.models import Order, OrderItem


@pytest.mark.django_db
def test_product_list_shows_active_products(client, product):
    response = client.get(reverse("shop:product-list"))
    assert response.status_code == 200
    assert product.name in response.content.decode()


@pytest.mark.django_db
def test_inactive_products_are_hidden(client, product):
    product.is_active = False
    product.save()
    assert client.get(product.get_absolute_url()).status_code == 404


@pytest.mark.django_db
def test_checkout_requires_an_email(client, product):
    response = client.post(reverse("shop:start-checkout", args=[product.slug]))
    assert response.status_code == 400
    assert not Order.objects.exists()


@pytest.mark.django_db
def test_checkout_creates_an_order_and_redirects_to_stripe(client, product):
    session = mock.Mock(id="cs_test_123", url="https://checkout.stripe.test/pay")
    with mock.patch("shop.billing.create_checkout_session", return_value=session) as create:
        response = client.post(
            reverse("shop:start-checkout", args=[product.slug]),
            {"email": "buyer@example.com"},
        )

    assert response.status_code == 302
    assert response["Location"] == "https://checkout.stripe.test/pay"
    create.assert_called_once()

    order = Order.objects.get()
    assert order.email == "buyer@example.com"
    assert order.status == Order.Status.PENDING
    assert order.total == product.price
    assert order.items.count() == 1


@pytest.mark.django_db
def test_webhook_marks_the_order_paid(client, product):
    order = Order.objects.create(email="buyer@example.com", total=product.price)
    OrderItem.objects.create(
        order=order, product=product, name=product.name, unit_price=product.price
    )
    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": str(order.reference),
                "payment_intent": "pi_test_123",
            }
        },
    }

    with mock.patch("shop.billing.construct_webhook_event", return_value=event):
        response = client.post(
            reverse("shop:stripe-webhook"),
            data=b"{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=1,v1=deadbeef",
        )

    assert response.status_code == 200
    order.refresh_from_db()
    assert order.status == Order.Status.PAID
    assert order.stripe_payment_intent == "pi_test_123"


@pytest.mark.django_db
def test_webhook_rejects_a_bad_signature(client):
    with mock.patch("shop.billing.construct_webhook_event", side_effect=ValueError("nope")):
        response = client.post(
            reverse("shop:stripe-webhook"), data=b"{}", content_type="application/json"
        )
    assert response.status_code == 400


@pytest.mark.django_db
def test_order_total_is_recalculated_from_items(product):
    order = Order.objects.create(email="buyer@example.com")
    OrderItem.objects.create(
        order=order, product=product, name=product.name, unit_price=product.price, quantity=3
    )
    assert order.recalculate_total() == Decimal("54.00")
