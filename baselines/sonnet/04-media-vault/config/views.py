import redis
import structlog
from django.conf import settings
from django.db import connection
from django.http import HttpRequest, HttpResponse

logger = structlog.get_logger(__name__)


def healthz(request: HttpRequest) -> HttpResponse:
    """Liveness check: the process is up and can serve requests."""
    return HttpResponse("ok")


def readyz(request: HttpRequest) -> HttpResponse:
    """Readiness check: dependencies (database, redis) are reachable."""
    try:
        connection.ensure_connection()
    except Exception:
        logger.exception("readyz_database_unreachable")
        return HttpResponse("not ready", status=503)

    try:
        redis.Redis.from_url(settings.REDIS_URL).ping()
    except Exception:
        logger.exception("readyz_redis_unreachable")
        return HttpResponse("not ready", status=503)

    return HttpResponse("ready")
