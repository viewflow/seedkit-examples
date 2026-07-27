from django.urls import path

from jobs.consumers import EchoConsumer

websocket_urlpatterns = [
    path("ws/echo/", EchoConsumer.as_asgi()),  # type: ignore[arg-type]
    # django-stubs has no model for ASGI views in `path()`; the type: ignore keeps pyright clean.
]
