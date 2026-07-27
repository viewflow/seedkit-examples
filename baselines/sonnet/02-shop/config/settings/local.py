"""Local development settings."""
from .base import *  # noqa: F403
from .base import INSTALLED_APPS, MIDDLEWARE

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += ["django_browser_reload"]

MIDDLEWARE += ["django_browser_reload.middleware.BrowserReloadMiddleware"]

# django-axes locks out real logins during local iteration; keep it off by default.
AXES_ENABLED = False

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Allow browser-reload / tailwind-cli to run without extra network calls.
INTERNAL_IPS = ["127.0.0.1"]
