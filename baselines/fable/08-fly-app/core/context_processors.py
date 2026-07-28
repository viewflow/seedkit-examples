from django.conf import settings
from django.http import HttpRequest


def analytics(request: HttpRequest) -> dict[str, str]:
    """Expose the GA4 measurement id to all templates."""
    return {"GA4_MEASUREMENT_ID": settings.GA4_MEASUREMENT_ID}
