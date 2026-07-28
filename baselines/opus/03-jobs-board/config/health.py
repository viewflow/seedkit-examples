"""Liveness and readiness endpoints.

These are deliberately plain-text and dependency-free so that a load balancer
or `docker healthcheck` can consume them without parsing.
"""

import logging

from django.db import connections, transaction
from django.http import HttpResponse
from django.views.decorators.cache import never_cache

logger = logging.getLogger(__name__)


# ATOMIC_REQUESTS would otherwise open a transaction just to answer a probe,
# which makes liveness depend on the database. Opt both probes out.
@transaction.non_atomic_requests
@never_cache
def healthz(request):
    """Liveness: the process is up and can serve a request."""
    return HttpResponse("ok", content_type="text/plain")


@transaction.non_atomic_requests
@never_cache
def readyz(request):
    """Readiness: every backing service this app needs is reachable."""
    for name, check in (("database", _check_database), ("redis", _check_redis)):
        try:
            check()
        except Exception:
            logger.exception("Readiness check failed: %s", name)
            return HttpResponse(
                f"not ready: {name}", status=503, content_type="text/plain"
            )
    return HttpResponse("ready", content_type="text/plain")


def _check_database():
    with connections["default"].cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()


def _check_redis():
    import redis
    from django.conf import settings

    client = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
    try:
        client.ping()
    finally:
        client.close()
