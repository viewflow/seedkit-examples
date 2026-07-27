from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from billing import views as billing_views
from config.sitemaps import sitemaps
from config.views import liveness, readiness, robots_txt
from pages.views import IndexView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("healthz", liveness, name="healthz"),
    path("readyz", readiness, name="readyz"),
    path("robots.txt", robots_txt, name="robots"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("billing/checkout/", billing_views.create_checkout_session, name="billing-checkout"),
    path("billing/portal/", billing_views.customer_portal, name="billing-portal"),
    path("billing/webhook/", billing_views.stripe_webhook, name="stripe-webhook"),
]

# Checked via INSTALLED_APPS (only local.py adds it), not settings.DEBUG —
# the Docker build shims DJANGO_DEBUG=True against *production* settings for
# collectstatic/tailwind build, and that module never installs this dev-only app.
if "django_browser_reload" in settings.INSTALLED_APPS:
    urlpatterns += [path("__reload__/", include("django_browser_reload.urls"))]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
