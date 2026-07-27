from django.db import connection
from django.http import HttpResponse


def healthz(request):
    """Liveness probe: the process is up."""
    return HttpResponse("ok", content_type="text/plain")


def readyz(request):
    """Readiness probe: the process can serve traffic (DB reachable)."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return HttpResponse("ready", content_type="text/plain")


def robots_txt(request):
    lines = ["User-agent: *", "Allow: /", "", "Sitemap: /sitemap.xml"]
    return HttpResponse("\n".join(lines), content_type="text/plain")
