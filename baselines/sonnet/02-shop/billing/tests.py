from django.urls import reverse


def test_webhook_rejects_invalid_signature(client):
    response = client.post(
        reverse("billing:stripe-webhook"),
        data=b"{}",
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="invalid",
    )

    assert response.status_code == 400
