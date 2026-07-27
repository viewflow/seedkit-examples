import redis
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError
from django.http import HttpResponse


def healthz(request):
    return HttpResponse("ok", content_type="text/plain")


def readyz(request):
    try:
        connections["default"].cursor()
    except OperationalError:
        return HttpResponse("not ready", status=503, content_type="text/plain")

    try:
        redis.Redis.from_url(settings.REDIS_URL).ping()
    except redis.RedisError:
        return HttpResponse("not ready", status=503, content_type="text/plain")

    return HttpResponse("ready", content_type="text/plain")
