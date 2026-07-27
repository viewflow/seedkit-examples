"""
URL configuration for the config project.
"""
from django.contrib import admin
from django.urls import include, path

import api.urls
from config.views import healthz, readyz

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz', healthz, name='healthz'),
    path('readyz', readyz, name='readyz'),
    path(
        api.urls.router.prefix,
        include((api.urls.urlpatterns, 'api'), namespace='api'),
    ),
]
