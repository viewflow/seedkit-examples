from django.db import connection
from django.http import HttpResponse


def healthz(request):
    """Liveness check: the process is up."""
    return HttpResponse("ok", content_type="text/plain")


def readyz(request):
    """Readiness check: the process can talk to its database."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return HttpResponse("ready", content_type="text/plain")
