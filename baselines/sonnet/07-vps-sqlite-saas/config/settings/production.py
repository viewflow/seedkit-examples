"""Production settings: VPS + docker-compose + Caddy."""

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: F403
from .base import env

DEBUG = False

SECRET_KEY = env.str("SECRET_KEY")

# Email: SMTP via EMAIL_URL, e.g.
# smtp+tls://token:token@smtp.postmarkapp.com:587
vars().update(env.email_url("EMAIL_URL"))

# django-structlog: structured JSON in production.
LOGGING["handlers"]["console"]["formatter"] = "json_formatter"  # noqa: F405

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Sentry
sentry_dsn = env.str("SENTRY_DSN", default="")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[DjangoIntegration()],
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.0),
        send_default_pii=False,
        environment=env.str("SENTRY_ENVIRONMENT", default="production"),
    )
