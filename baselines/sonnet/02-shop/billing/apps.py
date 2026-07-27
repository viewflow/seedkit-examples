import stripe
from django.apps import AppConfig
from django.conf import settings


class BillingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "billing"

    def ready(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
