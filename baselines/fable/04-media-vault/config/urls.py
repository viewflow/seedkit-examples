"""Project URL configuration."""

from django.contrib import admin
from django.urls import include, path

from api.urls import router
from config import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", views.healthz, name="healthz"),
    path("readyz", views.readyz, name="readyz"),
    path(router.prefix, include((router.urls, "api"), namespace="api")),
]
