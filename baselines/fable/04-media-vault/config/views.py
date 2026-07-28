"""Health check endpoints."""

import redis
from django.conf import settings
from django.db import connections
from django.http import HttpRequest, HttpResponse


def healthz(request: HttpRequest) -> HttpResponse:
    """Liveness: the process is up and serving requests."""
    return HttpResponse("ok", content_type="text/plain")


def readyz(request: HttpRequest) -> HttpResponse:
    """Readiness: PostgreSQL and Redis are both reachable."""
    try:
        connections["default"].ensure_connection()
        client = redis.Redis.from_url(settings.REDIS_URL)
        try:
            client.ping()
        finally:
            client.close()
    except Exception:
        return HttpResponse("unavailable", status=503, content_type="text/plain")
    return HttpResponse("ready", content_type="text/plain")
