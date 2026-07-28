from django.contrib import admin
from django.urls import include, path

from .views import healthz, readyz

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("mailauth.urls")),
    path("healthz", healthz),
    path("readyz", readyz),
]
