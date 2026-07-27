from django.db import connections
from django.http import HttpResponse
from django.shortcuts import render
from silk.profiling.profiler import silk_profile


@silk_profile(name="Home")
def home(request):
    return render(request, "home.html")


def healthz(request):
    return HttpResponse("ok", content_type="text/plain")


def readyz(request):
    with connections["default"].cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    return HttpResponse("ready", content_type="text/plain")
