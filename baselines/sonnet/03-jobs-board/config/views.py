from django.db import connection
from django.http import HttpResponse


def healthz(request):
    """Liveness probe: the process is up and can serve requests."""
    return HttpResponse("ok", content_type="text/plain")


def readyz(request):
    """Readiness probe: dependencies the app needs are reachable."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return HttpResponse("ready", content_type="text/plain")
