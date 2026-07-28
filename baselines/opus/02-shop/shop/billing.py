"""Thin wrapper around the Stripe SDK.

Everything Stripe-specific lives here so views stay readable and tests can patch
a single seam.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import stripe
from django.conf import settings
from django.urls import reverse

from shop.models import Order

if TYPE_CHECKING:
    from stripe.params.checkout._session_create_params import (
        SessionCreateParams,
        SessionCreateParamsLineItem,
    )

logger = logging.getLogger(__name__)


def _client() -> stripe.StripeClient:
    if not settings.STRIPE_SECRET_KEY:
        raise RuntimeError("STRIPE_SECRET_KEY is not configured.")
    return stripe.StripeClient(settings.STRIPE_SECRET_KEY)


def create_checkout_session(order: Order) -> stripe.checkout.Session:
    """Create a Stripe Checkout session for an order and remember its id."""
    line_items: list[SessionCreateParamsLineItem] = [
        {
            "price_data": {
                "currency": order.currency,
                "unit_amount": int(item.unit_price * 100),
                "product_data": {"name": item.name},
            },
            "quantity": item.quantity,
        }
        for item in order.items.all()
    ]

    params: SessionCreateParams = {
        "mode": "payment",
        "line_items": line_items,
        "customer_email": order.email,
        "client_reference_id": str(order.reference),
        "success_url": settings.SITE_URL + reverse("shop:checkout-success"),
        "cancel_url": settings.SITE_URL + reverse("shop:checkout-cancel"),
    }
    session = _client().checkout.sessions.create(params=params)
    order.stripe_session_id = session.id
    order.save(update_fields=["stripe_session_id", "updated_at"])
    return session


def construct_webhook_event(payload: bytes, signature: str) -> stripe.Event:
    """Verify a webhook signature and return the parsed event."""
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise RuntimeError("STRIPE_WEBHOOK_SECRET is not configured.")
    return stripe.Webhook.construct_event(payload, signature, settings.STRIPE_WEBHOOK_SECRET)


def handle_event(event: stripe.Event) -> None:
    """Apply a verified Stripe event to the matching order."""
    if event["type"] != "checkout.session.completed":
        logger.info("Ignoring Stripe event %s", event["type"])
        return

    session: dict[str, Any] = event["data"]["object"]
    reference = session.get("client_reference_id")
    order = Order.objects.filter(reference=reference).first()
    if order is None:
        logger.warning("Stripe event for unknown order reference %s", reference)
        return

    order.status = Order.Status.PAID
    order.stripe_payment_intent = session.get("payment_intent") or ""
    order.save(update_fields=["status", "stripe_payment_intent", "updated_at"])
    logger.info("Order %s marked paid", order.reference)
