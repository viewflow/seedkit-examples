from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse


def healthz(request):
    try:
        connections["default"].cursor()
    except OperationalError:
        return JsonResponse({"status": "error", "database": "down"}, status=503)
    return JsonResponse({"status": "ok"})
