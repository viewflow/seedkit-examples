from django.urls import re_path

from config.consumers import EchoConsumer

websocket_urlpatterns = [
    # django-stubs types `re_path`'s view param for sync HTTP views; channels'
    # ASGI consumers are a legitimate but differently-typed use of the same call.
    re_path(r"^ws/echo/$", EchoConsumer.as_asgi()),  # pyright: ignore[reportCallIssue, reportArgumentType]
]
