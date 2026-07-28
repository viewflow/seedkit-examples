from typing import cast

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import connection
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView


def healthz(request: HttpRequest) -> HttpResponse:
    """Liveness probe: the process is up."""
    return HttpResponse("ok", content_type="text/plain")


def readyz(request: HttpRequest) -> HttpResponse:
    """Readiness probe: database and cache are reachable."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        cache.set("readyz", "1", timeout=5)
    except Exception:  # noqa: BLE001 — any backend failure means "not ready"
        return HttpResponse("unavailable", content_type="text/plain", status=503)
    return HttpResponse("ready", content_type="text/plain")


class IndexView(TemplateView):
    template_name = "core/index.html"


class PrivacyView(LoginRequiredMixin, TemplateView):
    template_name = "core/privacy.html"


@login_required
def export_user_data(request: HttpRequest) -> JsonResponse:
    """GDPR data portability: everything stored about the signed-in user."""
    user = cast(User, request.user)
    payload = {
        "id": user.pk,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "date_joined": user.date_joined.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }
    response = JsonResponse(payload)
    response["Content-Disposition"] = 'attachment; filename="user-data.json"'
    return response


@login_required
@require_POST
def delete_account(request: HttpRequest) -> HttpResponse:
    """GDPR right to erasure: delete the signed-in user's account."""
    user = cast(User, request.user)
    logout(request)
    user.delete()
    return redirect("/")
