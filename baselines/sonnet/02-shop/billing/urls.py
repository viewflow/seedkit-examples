from django.urls import path

from billing.views import create_checkout_session, stripe_webhook

app_name = "billing"

urlpatterns = [
    path("checkout/", create_checkout_session, name="checkout"),
    path("webhook/", stripe_webhook, name="webhook"),
]
