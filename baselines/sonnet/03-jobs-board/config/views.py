from django.db import connections
from django.db.utils import OperationalError
from django.http import HttpResponse, HttpResponseServerError


def healthz(request):
    """Liveness probe: the process is up and can serve requests."""
    return HttpResponse("ok", content_type="text/plain")


def readyz(request):
    """Readiness probe: the process can reach its database."""
    try:
        connections["default"].cursor()
    except OperationalError:
        return HttpResponseServerError("not ready", content_type="text/plain")
    return HttpResponse("ready", content_type="text/plain")
