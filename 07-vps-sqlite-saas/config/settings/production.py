from .base import *

# SQLite production tuning — requires Django 5.1+ for `transaction_mode` / `init_command`.
DATABASES["default"]["OPTIONS"] = {
    "transaction_mode": "IMMEDIATE",  # avoid SQLITE_BUSY under concurrent writers
    "timeout": 5,  # seconds to wait on a locked DB
    "init_command": (
        "PRAGMA journal_mode=WAL;"  # writers don't block readers
        "PRAGMA synchronous=NORMAL;"  # safe with WAL, much faster than FULL
        "PRAGMA mmap_size=134217728;"  # 128 MiB memory-mapped reads
        "PRAGMA journal_size_limit=27103364;"
        "PRAGMA cache_size=2000;"  # pages (~ 8 MiB)
    ),
}
DATABASES["cache"]["OPTIONS"] = DATABASES["default"]["OPTIONS"]

# HTTPS — env-toggle so smoke / staging / direct-gunicorn access can run
# without TLS. Hardcoding True returns 301 on every plain-HTTP probe.
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
# Exempt healthcheck endpoints — internal probes hit the container directly
# without traversing the TLS proxy, so they arrive as plain HTTP and would be
# 301-redirected, making the probe never see 200.
SECURE_REDIRECT_EXEMPT = [r"^healthz$", r"^readyz$"]

# X-Forwarded-Proto trust. ONLY enable when there's a TLS-terminating proxy
# (Caddy here) in front of gunicorn. Without one, any client on the open port
# can spoof X-Forwarded-Proto: https and Django will treat the request as
# secure — bypassing SECURE_SSL_REDIRECT and CSRF cookie protections.
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
SECURE_CONTENT_TYPE_NOSNIFF = True  # Django default but worth being explicit

# Required behind a TLS-terminating proxy whenever Django sees the request
# as HTTP. Without it, admin / allauth POSTs return 403 with "Origin
# checking failed".
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

# Content Security Policy
MIDDLEWARE = [*MIDDLEWARE, "csp.middleware.CSPMiddleware"]

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "script-src": ("'self'",),
        "style-src": (
            "'self'",
            "'unsafe-inline'",
        ),  # tighten by removing unsafe-inline once styles are externalized
        "img-src": ("'self'", "data:"),
        "font-src": ("'self'",),
        "connect-src": ("'self'",),
        "frame-ancestors": ("'none'",),
        "base-uri": ("'self'",),
        "form-action": ("'self'",),
    },
}

# WhiteNoise — insert directly after SecurityMiddleware, switch staticfiles to manifest storage
sec_idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
MIDDLEWARE.insert(sec_idx + 1, "whitenoise.middleware.WhiteNoiseMiddleware")

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# allauth — verification link only goes to stdout with console email, so this
# is safe in prod (real SMTP) but would be painful for local signup.
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

# 2FA — allauth.mfa. Only force 2FA in prod; leave it optional in dev so
# seeded superusers can log in.
MFA_TOTP_ISSUER = env("DJANGO_SITE_DOMAIN", default="example.com")
MFA_SUPPORTED_TYPES = ["totp", "recovery_codes"]
ACCOUNT_REAUTHENTICATION_REQUIRED = True

# Error reporting — Sentry SaaS
SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        release=env("SENTRY_RELEASE", default=None),
    )
