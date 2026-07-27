from django.urls import path

from billing.views import stripe_webhook

app_name = "billing"

urlpatterns = [
    path("webhook/", stripe_webhook, name="stripe-webhook"),
]
