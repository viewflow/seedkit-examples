from django.contrib import admin
from django.urls import include, path

from .views import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("healthz/", health_check, name="health_check"),
]
