from django.db import connection
from django.http import HttpResponse, JsonResponse


def healthz(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as exc:
        return JsonResponse({"status": "error", "detail": str(exc)}, status=503)
    return HttpResponse("OK")
