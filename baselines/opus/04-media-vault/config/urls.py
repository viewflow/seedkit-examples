"""Root URLconf. WebSocket routes live in ``config/routing.py``."""

from django.contrib import admin
from django.urls import include, path
from dmr.openapi import build_schema
from dmr.openapi.views import OpenAPIJsonView

from api.urls import router as api_router
from config.health import healthz, readyz

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", healthz, name="healthz"),
    path("readyz", readyz, name="readyz"),
    path("django-rq/", include("django_rq.urls")),
    # Must precede the router include, which otherwise claims the whole
    # `api/` prefix. Only the JSON schema is served: the HTML doc viewers
    # need `dmr`'s templates, which requires it in INSTALLED_APPS.
    path(
        "api/openapi.json",
        OpenAPIJsonView.as_view(schema=build_schema(api_router)),
        name="openapi-schema",
    ),
    path(api_router.prefix, include((api_router.urls, "api"), namespace="api")),
]
