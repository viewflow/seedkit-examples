from django.conf import settings


def analytics(request):
    return {"GOATCOUNTER_URL": settings.GOATCOUNTER_URL}
