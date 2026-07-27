"""Local development settings."""
from .base import *  # noqa: F403
from .base import MIDDLEWARE, env

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
INTERNAL_IPS = ["127.0.0.1"]

MIDDLEWARE = [*MIDDLEWARE, "django_browser_reload.middleware.BrowserReloadMiddleware"]

EMAIL_BACKEND = env.str(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)

# Relax lockouts and slow hashing during local development.
AXES_ENABLED = False
