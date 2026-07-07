"""Production settings: Fly.io deploy target."""

import sentry_sdk
from csp.constants import NONCE, SELF
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: F403
from .base import env

DEBUG = False

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])  # pyright: ignore[reportArgumentType]


# Django security settings
# https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# Fly.io terminates TLS at the edge and forwards over HTTP with this header.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True


# Content Security Policy

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": [SELF],
        "script-src": [SELF, NONCE, "https://www.googletagmanager.com", "https://www.google-analytics.com"],
        "connect-src": [SELF, "https://www.google-analytics.com"],
        "img-src": [SELF, "https://www.google-analytics.com", "data:"],
        "style-src": [SELF],
        "frame-ancestors": [SELF],
    },
}


# Email: Anymail / Postmark

EMAIL_BACKEND = "anymail.backends.postmark.EmailBackend"


# Error reporting: GlitchTip (Sentry-protocol compatible)


def strip_user_pii(event, hint):
    """Scrub PII from error events before they leave the process (GDPR)."""
    user = event.get("user")
    if user:
        user.pop("email", None)
        user.pop("username", None)
        user.pop("ip_address", None)
    return event


sentry_sdk.init(
    dsn=GLITCHTIP_DSN or None,  # noqa: F405
    integrations=[DjangoIntegration(), CeleryIntegration()],
    send_default_pii=False,
    before_send=strip_user_pii,
    traces_sample_rate=env.float("GLITCHTIP_TRACES_SAMPLE_RATE", default=0.0),
    environment=env.str("FLY_APP_NAME", default="production"),
)
