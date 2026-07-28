"""Health-check endpoints for the reverse proxy and orchestration."""

from django.core.cache import cache
from django.db import connections
from django.http import HttpRequest, HttpResponse, HttpResponseServerError
from django.views.decorators.cache import never_cache


@never_cache
def healthz(request: HttpRequest) -> HttpResponse:
    """Liveness: the process is up and serving requests."""
    return HttpResponse("ok", content_type="text/plain")


@never_cache
def readyz(request: HttpRequest) -> HttpResponse:
    """Readiness: the database and cache are reachable."""
    try:
        for alias in ("default", "cache"):
            with connections[alias].cursor() as cursor:
                cursor.execute("SELECT 1")
        cache.set("readyz_probe", "1", timeout=5)
    except Exception:
        return HttpResponseServerError("not ready", content_type="text/plain")
    return HttpResponse("ready", content_type="text/plain")
