from django.conf import settings


def goatcounter(request):
    return {"GOATCOUNTER_SITE": settings.GOATCOUNTER_SITE}
