"""WebSocket URL routing (the ASGI counterpart of ``config/urls.py``)."""

from typing import Any, cast

from django.urls import path

from config.consumers import EchoConsumer

websocket_urlpatterns = [
    # `path()` is typed for HTTP views; a consumer is an ASGI app, so the
    # signature does not line up even though channels resolves it fine.
    path("ws/echo/", cast(Any, EchoConsumer.as_asgi()), name="ws-echo"),
]
