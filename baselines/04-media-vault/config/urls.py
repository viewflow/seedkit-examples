"""URL configuration for the config project."""

from django.contrib import admin
from django.urls import include, path

from api.urls import router as api_router
from core.views import healthcheck

urlpatterns = [
    path('admin/', admin.site.urls),
    path('django-rq/', include('django_rq.urls')),
    path('healthz/', healthcheck, name='healthcheck'),
    path(
        api_router.prefix,
        include((api_router.urls, 'api'), namespace='api'),
    ),
]
