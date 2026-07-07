"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import include, path

from config.health import healthz

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("mailauth.urls")),
    path("healthz/", healthz, name="healthz"),
]
