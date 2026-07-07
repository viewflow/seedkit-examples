import sentry_sdk
import structlog
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])


# Django security settings
# https://docs.djangoproject.com/en/6.0/topics/security/

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# App sits behind a reverse proxy that terminates TLS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# GDPR: retention defaults
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 2 weeks
DBBACKUP_CLEANUP_KEEP = 14
DBBACKUP_CLEANUP_KEEP_MEDIA = 14


# structlog: JSON logs in production

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json_formatter",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}


# Bugsink (self-hosted, Sentry-protocol compatible) error reporting
# GDPR: PII is scrubbed before events ever leave the process.

SENTRY_DSN = env.str("SENTRY_DSN", default="")


def _scrub_pii(event, hint):
    request = event.get("request")
    if request:
        request.pop("cookies", None)
        headers = request.get("headers")
        if headers:
            headers.pop("Authorization", None)
            headers.pop("Cookie", None)
    user = event.get("user")
    if user:
        user.pop("email", None)
        user.pop("username", None)
        user.pop("ip_address", None)
    return event


if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        send_default_pii=False,
        before_send=_scrub_pii,
        traces_sample_rate=0.0,
    )
