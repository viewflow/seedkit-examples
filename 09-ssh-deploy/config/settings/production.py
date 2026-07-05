from .base import *

# Security
# https://docs.djangoproject.com/en/stable/topics/security/

# HTTPS — env-toggle so smoke / staging / direct-gunicorn access can run
# without TLS. Hardcoding True returns 301 on every plain-HTTP probe.
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
# Exempt healthcheck endpoints — managed-platform internal probes hit the
# container directly without traversing the TLS proxy, so they arrive as
# plain HTTP and would be 301-redirected, making the probe never see 200.
SECURE_REDIRECT_EXEMPT = [r"^healthz$", r"^readyz$"]

# X-Forwarded-Proto trust. ONLY enable when there's a TLS-terminating proxy
# (Caddy in front of gunicorn). Without one, any client on the open port
# can spoof X-Forwarded-Proto: https and Django will treat the request as
# secure — bypassing SECURE_SSL_REDIRECT and CSRF cookie protections.
if env.bool("DJANGO_BEHIND_PROXY", default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = False  # opt in only after every subdomain serves HTTPS
SECURE_HSTS_PRELOAD = False  # opt in only after manual review of the consequences

# These two are deliberate opt-outs above, so silence the matching
# `manage.py check --deploy` warnings.
SILENCED_SYSTEM_CHECKS = ["security.W005", "security.W021"]

# Other browser hardening
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True  # Django default but worth being explicit

# Required behind a TLS-terminating proxy whenever Django sees the request
# as HTTP. Without it, admin POSTs return 403 with "Origin checking failed".
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])


# Content Security Policy — django-csp
# https://django-csp.readthedocs.io/
MIDDLEWARE = [*MIDDLEWARE, "csp.middleware.CSPMiddleware"]

# ANALYTICS_HOST comes from `from .base import *` — Umami is self-hosted and env-driven.
_UMAMI = (ANALYTICS_HOST,) if ANALYTICS_HOST else ()

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "script-src": ("'self'", *_UMAMI),
        "style-src": ("'self'", "'unsafe-inline'"),  # tighten once styles are externalized
        "img-src": ("'self'", "data:"),
        "font-src": ("'self'",),
        "connect-src": ("'self'", *_UMAMI),
        "frame-ancestors": ("'none'",),
        "base-uri": ("'self'",),
        "form-action": ("'self'",),
    },
}


# Error reporting — Bugsink (self-hosted, Sentry-protocol)
# https://www.bugsink.com/docs/
SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    def _scrub(event, hint):
        request = event.get("request") or {}
        headers = request.get("headers") or {}
        for h in ("Authorization", "Cookie"):
            headers.pop(h, None)
        return event

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        release=env("SENTRY_RELEASE", default=None),
        send_default_pii=False,
        before_send=_scrub,
    )


# Database backups — django-dbbackup
# Wrapped in `if not DEBUG` — the Dockerfile build runs collectstatic with
# DJANGO_DEBUG=True, and dbbackup in INSTALLED_APPS unconditionally would
# evaluate env("AWS_ACCESS_KEY_ID") (no default) and crash the build.
if not DEBUG:
    INSTALLED_APPS = [*INSTALLED_APPS, "dbbackup"]

    DBBACKUP_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    DBBACKUP_STORAGE_OPTIONS = {
        "access_key": env("AWS_ACCESS_KEY_ID"),
        "secret_key": env("AWS_SECRET_ACCESS_KEY"),
        "bucket_name": env("DBBACKUP_BUCKET"),  # SEPARATE bucket from media — different lifecycle
        "default_acl": "private",
    }

    DBBACKUP_CLEANUP_KEEP = 14  # daily backups retained
    DBBACKUP_CLEANUP_KEEP_MEDIA = 7
    DBBACKUP_FILENAME_TEMPLATE = "{databasename}-{servername}-{datetime}.{extension}"
