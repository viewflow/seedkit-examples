from unittest.mock import Mock, patch

import pytest
import stripe
from django.urls import reverse


@pytest.mark.django_db
class TestCreateCheckoutSession:
    @patch("billing.views.stripe.checkout.Session.create")
    def test_creates_session(self, mock_create, client):
        mock_create.return_value = Mock(id="cs_test_123", url="https://checkout.stripe.com/cs_test_123")

        response = client.post(reverse("billing:checkout"), {"price_id": "price_123"})

        assert response.status_code == 200
        assert response.json() == {"id": "cs_test_123", "url": "https://checkout.stripe.com/cs_test_123"}
        mock_create.assert_called_once()


@pytest.mark.django_db
class TestStripeWebhook:
    @patch("billing.views.stripe.Webhook.construct_event")
    def test_valid_event(self, mock_construct_event, client):
        mock_construct_event.return_value = {"type": "checkout.session.completed"}

        response = client.post(
            reverse("billing:webhook"),
            data=b"{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=1,v1=fake",
        )

        assert response.status_code == 200

    @patch("billing.views.stripe.Webhook.construct_event")
    def test_invalid_signature(self, mock_construct_event, client):
        mock_construct_event.side_effect = stripe.SignatureVerificationError("bad signature", "sig_header")

        response = client.post(
            reverse("billing:webhook"),
            data=b"{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=1,v1=bad",
        )

        assert response.status_code == 400
