"""API-only URLconf for the django-bolt process — no admin, no accounts.

Bolt routes live in `api/api.py`; this urlconf only keeps a liveness probe
reachable through the Django fallback.
"""

from django.urls import path

from core import views

urlpatterns = [
    path("healthz", views.healthz, name="healthz"),
]
