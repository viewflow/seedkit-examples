"""WebSocket URL routing."""

from django.urls import path

from config.consumers import EchoConsumer

# django-stubs types path() for HTTP views only; Channels routes ASGI apps.
websocket_urlpatterns = [
    path("ws/echo/", EchoConsumer.as_asgi()),  # pyright: ignore[reportCallIssue, reportArgumentType]
]
