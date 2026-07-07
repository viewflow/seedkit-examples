import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: F403
from .base import env

DEBUG = False

# Security
# https://docs.djangoproject.com/en/5.1/topics/security/

SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=60 * 60 * 24 * 30)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Caddy terminates TLS and forwards over plain HTTP within the docker network,
# setting this header so Django knows the original request was HTTPS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Content-Security-Policy via django-csp
# https://django-csp.readthedocs.io/

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "img-src": ["'self'", "data:"],
        "style-src": ["'self'"],
        "script-src": ["'self'"],
        "frame-ancestors": ["'none'"],
    },
}

# Sentry
# https://docs.sentry.io/platforms/python/integrations/django/

SENTRY_DSN = env.str("SENTRY_DSN", default="")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.0),
        send_default_pii=False,
        environment=env.str("SENTRY_ENVIRONMENT", default="production"),
    )

# JSON logs in production
LOGGING["handlers"]["console"]["formatter"] = "json_formatter"  # noqa: F405
