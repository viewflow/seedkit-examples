"""Health check endpoints."""

from django.db import DatabaseError, connections
from django.http import HttpResponse, HttpResponseServerError


def healthz(request):
    """Liveness probe: the process is up and serving requests."""
    return HttpResponse("ok", content_type="text/plain")


def readyz(request):
    """Readiness probe: the database is reachable."""
    try:
        connections["default"].cursor().execute("SELECT 1")
    except DatabaseError:
        return HttpResponseServerError("database unavailable", content_type="text/plain")
    return HttpResponse("ready", content_type="text/plain")
