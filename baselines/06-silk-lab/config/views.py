from django.db import DatabaseError, connection
from django.http import JsonResponse
from django_tasks_db.models import DBTaskResult
from silk.profiling.profiler import silk_profile


@silk_profile(name="Recent task results")
def recent_task_results(request):
    """Demo view profiled with django-silk: lists the latest background task runs."""
    results = [
        {
            "id": str(result.id),
            "task_name": result.task_name,
            "status": result.status,
            "enqueued_at": result.enqueued_at.isoformat(),
        }
        for result in DBTaskResult.objects.order_by("-enqueued_at")[:20]
    ]
    return JsonResponse({"results": results})


def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        return JsonResponse({"status": "error", "database": "down"}, status=503)
    return JsonResponse({"status": "ok", "database": "up"})
