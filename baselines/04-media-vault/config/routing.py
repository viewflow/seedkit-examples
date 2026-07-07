from django.urls import re_path

from core.consumers import EchoConsumer

websocket_urlpatterns = [
    # django-stubs types re_path()'s second argument for HTTP views; Channels
    # consumers are ASGI applications, which pyright can't reconcile here.
    re_path(r'^ws/echo/$', EchoConsumer.as_asgi())  # pyright: ignore[reportCallIssue, reportArgumentType]
]
