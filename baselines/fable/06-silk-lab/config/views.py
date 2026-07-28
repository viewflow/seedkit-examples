from django.contrib.auth.models import User
from django.db import DatabaseError, connection
from django.http import HttpResponse
from django.shortcuts import render
from silk.profiling.profiler import silk_profile


@silk_profile(name="Home page")
def home(request):
    user_count = User.objects.count()
    return render(request, "home.html", {"user_count": user_count})


def healthz(request):
    """Liveness probe: the process is up."""
    return HttpResponse("ok", content_type="text/plain")


def readyz(request):
    """Readiness probe: the database is reachable."""
    try:
        connection.ensure_connection()
    except DatabaseError:
        return HttpResponse("database unavailable", status=503, content_type="text/plain")
    return HttpResponse("ready", content_type="text/plain")
