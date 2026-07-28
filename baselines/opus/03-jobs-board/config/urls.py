"""Root URL configuration."""

from django.contrib import admin
from django.urls import include, path

from config import health

urlpatterns = [
    path("", include("jobs.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("mailauth.urls")),
    # Probes stay outside any locale prefix so orchestrators can hit fixed paths.
    path("healthz", health.healthz, name="healthz"),
    path("readyz", health.readyz, name="readyz"),
    path("i18n/", include("django.conf.urls.i18n")),
]
