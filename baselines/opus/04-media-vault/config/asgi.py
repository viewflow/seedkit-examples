"""ASGI entrypoint: HTTP and WebSocket served from one application.

Run it with ``uvicorn config.asgi:application``. ``manage.py runserver`` will
*not* upgrade WebSocket connections, so use uvicorn even in development.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

# The HTTP application has to be built (and therefore the app registry
# populated) before the consumer modules are imported below.
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.security.websocket import AllowedHostsOriginValidator  # noqa: E402

from config.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
        ),
    },
)
