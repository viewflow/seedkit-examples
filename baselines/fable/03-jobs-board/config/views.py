from django.db import connections
from django.http import HttpResponse, JsonResponse


def healthz(request):
    """Liveness probe: the process is up."""
    return HttpResponse("ok", content_type="text/plain")


def readyz(request):
    """Readiness probe: the database is reachable."""
    try:
        connections["default"].cursor().execute("SELECT 1")
    except Exception:
        return JsonResponse({"status": "database unavailable"}, status=503)
    return HttpResponse("ready", content_type="text/plain")
