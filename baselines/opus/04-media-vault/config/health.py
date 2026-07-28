"""Liveness and readiness probes.

``/healthz`` answers "is this process alive?" and touches nothing external, so
an orchestrator never restarts a healthy pod because Postgres hiccuped.
``/readyz`` answers "can this process serve traffic?" and does check the
backing services.
"""

import structlog
from django.core.cache import cache
from django.db import connections
from django.http import HttpRequest, HttpResponse

logger = structlog.get_logger(__name__)

_READY_PROBE_KEY = "healthcheck:readyz"


def healthz(request: HttpRequest) -> HttpResponse:
    """Liveness: the process is up and the URLconf resolves."""
    return HttpResponse("ok", content_type="text/plain")


def readyz(request: HttpRequest) -> HttpResponse:
    """Readiness: Postgres and Redis are both reachable."""
    checks = {"database": _check_database, "redis": _check_redis}
    failed = []

    for name, check in checks.items():
        try:
            check()
        # Any failure at all means "not ready" — never let a probe raise.
        except Exception as exc:
            logger.warning("healthcheck.failed", component=name, error=str(exc))
            failed.append(name)

    if failed:
        return HttpResponse(
            "not ready: " + ", ".join(failed),
            content_type="text/plain",
            status=503,
        )
    return HttpResponse("ready", content_type="text/plain")


def _check_database() -> None:
    with connections["default"].cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()


def _check_redis() -> None:
    cache.set(_READY_PROBE_KEY, "1", timeout=10)
    if cache.get(_READY_PROBE_KEY) != "1":
        raise RuntimeError("redis round-trip returned unexpected value")
