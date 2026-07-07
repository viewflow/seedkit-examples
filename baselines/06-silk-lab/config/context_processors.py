from django.conf import settings


def analytics(request):
    return {"goatcounter_site_code": settings.GOATCOUNTER_SITE_CODE}
