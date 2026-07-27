"""Local development settings."""

from .base import *  # noqa: F403

DEBUG = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# django-structlog: pretty console output while developing.
LOGGING["handlers"]["console"]["formatter"] = "plain_console"  # noqa: F405

# django-axes locks out fast in prod; keep local dev friction-free.
AXES_ENABLED = False
