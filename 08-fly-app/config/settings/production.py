from .base import *

# --- Security ---
# HTTPS — env-toggle so smoke / staging / direct-gunicorn access can run
# without TLS. Hardcoding True returns 301 on every plain-HTTP probe.
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
# Exempt healthcheck endpoints — managed-platform internal probes (Fly,
# Railway, k8s) hit the container directly without traversing the TLS
# proxy, so they arrive as plain HTTP and would be 301-redirected, making
# the probe never see 200.
SECURE_REDIRECT_EXEMPT = [r"^healthz$", r"^readyz$"]

# X-Forwarded-Proto trust. ONLY enable when there's a TLS-terminating proxy
# (Fly's edge) in front of gunicorn.
if env.bool("DJANGO_BEHIND_PROXY", default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = False  # opt in only after every subdomain serves HTTPS
SECURE_HSTS_PRELOAD = False  # opt in only after manual review of the consequences

# These two are deliberate opt-outs above, so silence the matching
# `manage.py check --deploy` warnings.
SILENCED_SYSTEM_CHECKS = ["security.W005", "security.W021"]

# Other browser hardening
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True

# Required behind a TLS-terminating proxy whenever Django sees the request
# as HTTP. Without it, admin / allauth POSTs return 403 with "Origin
# checking failed".
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])


# --- Content Security Policy — django-csp ---
MIDDLEWARE = [*MIDDLEWARE, "csp.middleware.CSPMiddleware"]

_GA4_HOSTS = ("https://www.googletagmanager.com", "https://www.google-analytics.com")
_UMAMI = (ANALYTICS_HOST,) if ANALYTICS_HOST else ()
_S3_HOST = (AWS_S3_ENDPOINT_URL,) if AWS_S3_ENDPOINT_URL else ()

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "script-src": ("'self'", *_GA4_HOSTS, *_UMAMI),
        "style-src": ("'self'", "'unsafe-inline'"),  # tighten once styles are externalized
        "img-src": ("'self'", "data:", *_GA4_HOSTS, *_S3_HOST),
        "font-src": ("'self'",),
        "connect-src": ("'self'", *_GA4_HOSTS, *_UMAMI),
        "frame-ancestors": ("'none'",),
        "base-uri": ("'self'",),
        "form-action": ("'self'",),
    },
}


# --- Storage: flip static to S3 ---
# Guard with `if AWS_STORAGE_BUCKET_NAME:` so a config that loads
# production.py in dev (where the bucket env may be empty) still boots via
# the base.py FileSystemStorage fallback.
if AWS_STORAGE_BUCKET_NAME:
    STORAGES = {
        **STORAGES,
        "staticfiles": {
            "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
            "OPTIONS": {"location": "static"},
        },
    }

    if AWS_S3_CUSTOM_DOMAIN:
        STATIC_URL = f"{AWS_S3_URL_PROTOCOL}//{AWS_S3_CUSTOM_DOMAIN}/static/"
    elif AWS_S3_ENDPOINT_URL:
        STATIC_URL = f"{AWS_S3_ENDPOINT_URL.rstrip('/')}/{AWS_STORAGE_BUCKET_NAME}/static/"
    else:
        _region = "" if AWS_S3_REGION_NAME == "us-east-1" else f".{AWS_S3_REGION_NAME}"
        STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3{_region}.amazonaws.com/static/"


# --- django-axes: cache handler when Redis is in scope ---
AXES_HANDLER = "axes.handlers.cache.AxesCacheHandler"


# --- Error reporting: GlitchTip (Sentry-protocol) via sentry-sdk ---
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

    # Browser-side SDK isn't wired here (server-side only), but the ingest
    # host still needs a CSP allowance if a front-end SDK is added later.
    _sentry_host = f"https://{SENTRY_DSN.split('@')[-1].split('/')[0]}"
    CONTENT_SECURITY_POLICY["DIRECTIVES"]["connect-src"] = (
        *CONTENT_SECURITY_POLICY["DIRECTIVES"]["connect-src"],
        _sentry_host,
    )
