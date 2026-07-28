import structlog
from django.db import connections
from django.http import HttpResponse
from django_rq import get_queue

logger = structlog.get_logger(__name__)


def healthz(request):
    """Liveness probe: the process is up and serving requests."""
    return HttpResponse("ok", content_type="text/plain")


def readyz(request):
    """Readiness probe: the app can reach its backing services."""
    try:
        connections["default"].ensure_connection()
        get_queue("default").connection.ping()
    except Exception:
        logger.exception("readiness_check_failed")
        return HttpResponse("unavailable", content_type="text/plain", status=503)
    return HttpResponse("ready", content_type="text/plain")
