from django.conf import settings
from django.db import connection
from django.db.utils import Error as DatabaseError
from django.http import JsonResponse
from redis import Redis
from redis.exceptions import RedisError


def healthcheck(request):
    errors = {}

    try:
        connection.ensure_connection()
    except DatabaseError as exc:
        errors['database'] = str(exc)

    try:
        Redis.from_url(settings.REDIS_URL).ping()
    except RedisError as exc:
        errors['redis'] = str(exc)

    if errors:
        return JsonResponse({'status': 'error', 'errors': errors}, status=503)
    return JsonResponse({'status': 'ok'})
