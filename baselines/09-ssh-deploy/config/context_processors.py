from django.conf import settings


def analytics(request):
    return {
        "UMAMI_WEBSITE_ID": settings.UMAMI_WEBSITE_ID,
        "UMAMI_HOST": settings.UMAMI_HOST,
    }
