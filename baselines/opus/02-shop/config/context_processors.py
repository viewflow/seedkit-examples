"""Template context shared by every page (SEO defaults, Stripe public key)."""

from django.conf import settings
from django.http import HttpRequest


def site(request: HttpRequest) -> dict[str, str]:
    """Expose site-wide metadata used by ``base.html`` for meta/OG tags."""
    return {
        "SITE_NAME": settings.SITE_NAME,
        "SITE_DESCRIPTION": settings.SITE_DESCRIPTION,
        "SITE_URL": settings.SITE_URL,
        "STRIPE_PUBLISHABLE_KEY": settings.STRIPE_PUBLISHABLE_KEY,
    }
