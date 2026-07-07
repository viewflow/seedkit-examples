from django.core.cache import cache
from django.db import connections
from django.http import JsonResponse


def health_check(request):
    """Liveness/readiness probe: verifies the default DB and cache DB respond."""
    checks = {}

    for alias in ("default", "cache"):
        try:
            with connections[alias].cursor() as cursor:
                cursor.execute("SELECT 1")
            checks[alias] = "ok"
        except Exception as exc:  # noqa: BLE001
            checks[alias] = f"error: {exc}"

    try:
        cache.set("healthcheck", "ok", timeout=5)
        checks["cache_backend"] = "ok" if cache.get("healthcheck") == "ok" else "error"
    except Exception as exc:  # noqa: BLE001
        checks["cache_backend"] = f"error: {exc}"

    healthy = all(value == "ok" for value in checks.values())
    status = 200 if healthy else 503
    return JsonResponse({"status": "ok" if healthy else "error", "checks": checks}, status=status)
