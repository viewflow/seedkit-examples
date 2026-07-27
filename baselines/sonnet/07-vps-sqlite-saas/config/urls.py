from django.contrib import admin
from django.urls import include, path

from config.views import healthz, readyz

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("healthz", healthz, name="healthz"),
    path("readyz", readyz, name="readyz"),
]
