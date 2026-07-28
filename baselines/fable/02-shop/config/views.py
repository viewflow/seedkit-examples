from django.db import connections
from django.db.utils import OperationalError
from django.http import HttpRequest, HttpResponse


def healthz(request: HttpRequest) -> HttpResponse:
    """Liveness probe."""
    return HttpResponse("ok", content_type="text/plain")


def readyz(request: HttpRequest) -> HttpResponse:
    """Readiness probe — verifies the database connection."""
    try:
        connections["default"].cursor()
    except OperationalError:
        return HttpResponse("database unavailable", status=503, content_type="text/plain")
    return HttpResponse("ready", content_type="text/plain")


def robots_txt(request: HttpRequest) -> HttpResponse:
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
