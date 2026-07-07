"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.
HTTP requests are served by Django as usual; WebSocket connections are routed
through Channels to the consumers declared in ``config.routing``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

django_asgi_app = get_asgi_application()

from config.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        'http': django_asgi_app,
        'websocket': AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
        ),
    }
)
