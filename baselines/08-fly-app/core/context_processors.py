from django.conf import settings


def analytics(request):
    return {"GA4_MEASUREMENT_ID": settings.GA4_MEASUREMENT_ID}
