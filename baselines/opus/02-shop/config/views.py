"""Infrastructure endpoints: health checks, robots.txt and error pages."""

from django.db import connections
from django.db.utils import OperationalError
from django.http import HttpRequest, HttpResponse
from django.views.decorators.cache import never_cache


@never_cache
def healthz(request: HttpRequest) -> HttpResponse:
    """Liveness probe — the process is up and can serve a request."""
    return HttpResponse("ok", content_type="text/plain")


@never_cache
def readyz(request: HttpRequest) -> HttpResponse:
    """Readiness probe — dependencies (the database) answer."""
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except OperationalError:
        return HttpResponse("not ready", content_type="text/plain", status=503)
    return HttpResponse("ready", content_type="text/plain")
