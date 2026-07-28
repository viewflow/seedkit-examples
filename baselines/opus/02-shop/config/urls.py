"""Root URL configuration."""

from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import URLPattern, URLResolver, include, path
from django.views.generic import TemplateView

from config.views import healthz, readyz
from pages.sitemaps import SITEMAPS

urlpatterns: list[URLPattern | URLResolver] = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("shop/", include("shop.urls")),
    # Infrastructure
    path("healthz", healthz, name="healthz"),
    path("readyz", readyz, name="readyz"),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots",
    ),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": SITEMAPS},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    # Public pages last so "" does not shadow anything above.
    path("", include("pages.urls")),
]

if settings.DEBUG:
    urlpatterns += [path("__reload__/", include("django_browser_reload.urls"))]

# Error handlers (rendered by Django when DEBUG is off).
handler403 = "django.views.defaults.permission_denied"
handler404 = "django.views.defaults.page_not_found"
handler500 = "django.views.defaults.server_error"
