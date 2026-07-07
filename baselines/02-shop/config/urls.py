"""
URL configuration for the shop project.
"""

from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.templatetags.static import static
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

from pages.sitemaps import StaticViewSitemap

from .health import healthz

sitemaps = {
    "static": StaticViewSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("pages.urls")),
    path("healthz/", healthz, name="healthz"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots",
    ),
    path(
        "favicon.ico",
        RedirectView.as_view(url=static("images/favicon.svg"), permanent=True),
    ),
]
