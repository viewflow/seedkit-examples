"""Production settings."""

import os

from .base import *  # noqa: F403
from .base import LOGGING

# Fail fast if the secret key was not provided.
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

DEBUG = False

CSRF_TRUSTED_ORIGINS = [
    o for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o
]

# Security hardening ---------------------------------------------------------
# TLS terminates at the reverse proxy in front of the app container.

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = os.environ.get("DJANGO_SECURE_SSL_REDIRECT", "true") == "true"
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"

# JSON logs in production.
LOGGING["handlers"]["console"]["formatter"] = "json"

# Error reporting: Bugsink (self-hosted, sentry-sdk compatible) ---------------

SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    from core.gdpr import scrub_sentry_event

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        environment=os.environ.get("SENTRY_ENVIRONMENT", "production"),
        release=os.environ.get("GIT_SHA", ""),
        # GDPR: never attach PII, and scrub what slips through.
        send_default_pii=False,
        before_send=scrub_sentry_event,
        # Bugsink is an error tracker; it does not ingest performance data.
        traces_sample_rate=0,
        max_request_body_size="never",
    )
