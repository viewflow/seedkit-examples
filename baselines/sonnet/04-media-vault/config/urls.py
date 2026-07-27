"""URL configuration for config project."""

from django.contrib import admin
from django.urls import include, path

from api.urls import router as api_router
from config.views import healthz, readyz

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", healthz),
    path("readyz", readyz),
    path(api_router.prefix, include((api_router.urls, "api"), namespace="api")),
]
