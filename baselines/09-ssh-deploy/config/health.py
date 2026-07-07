from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse
from redis import Redis
from redis.exceptions import RedisError


def healthz(request):
    """Liveness probe: process is up and can serve requests."""
    return JsonResponse({"status": "ok"})


def readyz(request):
    """Readiness probe: dependencies (database, redis) are reachable."""
    checks = {}

    try:
        connections["default"].cursor()
        checks["database"] = "ok"
    except OperationalError:
        checks["database"] = "error"

    try:
        Redis.from_url(settings.REDIS_URL).ping()
        checks["redis"] = "ok"
    except RedisError:
        checks["redis"] = "error"

    healthy = all(value == "ok" for value in checks.values())
    status = 200 if healthy else 503
    return JsonResponse({"status": "ok" if healthy else "error", "checks": checks}, status=status)
