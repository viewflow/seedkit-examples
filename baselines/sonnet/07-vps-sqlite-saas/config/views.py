from django.db import DatabaseError, connections
from django.http import HttpResponse


def healthz(request):
    """Liveness probe: process is up and serving requests."""
    return HttpResponse("ok", content_type="text/plain")


def readyz(request):
    """Readiness probe: dependencies (both sqlite databases) are reachable."""
    for alias in ("default", "cache"):
        try:
            connections[alias].cursor().execute("SELECT 1")
        except DatabaseError:
            return HttpResponse("not ready", content_type="text/plain", status=503)
    return HttpResponse("ready", content_type="text/plain")
