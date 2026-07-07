from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods


def index(request):
    return render(request, "core/index.html")


@require_http_methods(["GET"])
def health_check(request):
    checks = {}

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["database"] = f"error: {exc}"

    try:
        cache.set("healthz", "ok", timeout=5)
        checks["cache"] = "ok" if cache.get("healthz") == "ok" else "error: cache read/write mismatch"
    except Exception as exc:  # noqa: BLE001
        checks["cache"] = f"error: {exc}"

    healthy = all(value == "ok" for value in checks.values())
    return JsonResponse({"status": "ok" if healthy else "error", "checks": checks}, status=200 if healthy else 503)


@login_required
def data_export(request):
    """GDPR: let a user download the personal data we hold on them."""
    user = request.user
    return JsonResponse(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "date_joined": user.date_joined.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }
    )


@login_required
@require_http_methods(["GET", "POST"])
def data_delete(request):
    """GDPR: let a user erase their account and personal data."""
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        return redirect("index")
    return render(request, "core/data_delete_confirm.html")
