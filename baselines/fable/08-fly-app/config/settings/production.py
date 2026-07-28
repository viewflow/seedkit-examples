"""Production settings for Fly.io."""

import sentry_sdk
from csp.constants import NONE, SELF
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.scrubber import DEFAULT_DENYLIST, EventScrubber

from .base import *
from .base import ANYMAIL, MIDDLEWARE, env

DEBUG = False

SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[".fly.dev"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=["https://*.fly.dev"])

# Fly.io terminates TLS at the edge.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30  # bump to a year once the domain is stable
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Transactional email via Postmark (anymail). Console backend stays for dev.
EMAIL_BACKEND = "anymail.backends.postmark.EmailBackend"
ANYMAIL["POSTMARK_SERVER_TOKEN"] = env("POSTMARK_SERVER_TOKEN", default="")

# Real S3 unless an explicit endpoint (e.g. another S3-compatible store) is given.
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default=None)

# Content Security Policy (django-csp), GA4 domains allowed.
MIDDLEWARE = [*MIDDLEWARE, "csp.middleware.CSPMiddleware"]

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": [SELF],
        "script-src": [SELF, "https://www.googletagmanager.com"],
        "connect-src": [
            SELF,
            "https://*.google-analytics.com",
            "https://*.analytics.google.com",
            "https://*.googletagmanager.com",
        ],
        "img-src": [
            SELF,
            "data:",
            "https://*.google-analytics.com",
            "https://*.googletagmanager.com",
        ],
        "style-src": [SELF],
        "font-src": [SELF],
        "object-src": [NONE],
        "frame-ancestors": [NONE],
        "base-uri": [SELF],
        "form-action": [SELF],
        "upgrade-insecure-requests": True,
    },
}


def _scrub_pii(event, hint):
    """GDPR: strip user identity, cookies and client IPs from error reports."""
    event.pop("user", None)
    request = event.get("request") or {}
    request.pop("cookies", None)
    request.pop("env", None)
    headers = request.get("headers") or {}
    for header in ("Cookie", "Authorization", "X-Forwarded-For", "X-Real-Ip"):
        headers.pop(header, None)
    return event


# Error reporting to GlitchTip (Sentry-protocol compatible).
GLITCHTIP_DSN = env("GLITCHTIP_DSN", default=env("SENTRY_DSN", default=""))
if GLITCHTIP_DSN:
    sentry_sdk.init(
        dsn=GLITCHTIP_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        send_default_pii=False,
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.0),
        event_scrubber=EventScrubber(
            denylist=[*DEFAULT_DENYLIST, "email", "username", "phone", "address"],
            recursive=True,
        ),
        before_send=_scrub_pii,
        environment=env("SENTRY_ENVIRONMENT", default="production"),
    )
