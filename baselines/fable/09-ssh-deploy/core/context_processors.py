from django.conf import settings


def umami(request):
    """Expose self-hosted Umami analytics config to templates."""
    return {
        "UMAMI_HOST": settings.UMAMI_HOST,
        "UMAMI_WEBSITE_ID": settings.UMAMI_WEBSITE_ID,
    }
