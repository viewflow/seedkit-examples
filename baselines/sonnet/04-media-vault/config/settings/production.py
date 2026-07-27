"""Production settings. Deployment wiring (WSGI/ASGI server, TLS, etc.) is out of scope here."""

from config.settings._logging import build_logging_config
from config.settings.base import *  # noqa: F403
from config.settings.base import env

DEBUG = False

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

LOGGING = build_logging_config(json_logs=True)
