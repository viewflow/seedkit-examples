from .base import *

# WhiteNoise — static files only (references/storage-whitenoise.md)
sec_idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
MIDDLEWARE.insert(sec_idx + 1, "whitenoise.middleware.WhiteNoiseMiddleware")

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# django-allauth — tighten verification now that real SMTP is configured.
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

# Security (references/security.md)
# HTTPS — env-toggle so smoke / staging / direct-gunicorn access can run
# without TLS. Hardcoding True returns 301 on every plain-HTTP probe.
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
# Exempt healthcheck endpoints — managed-platform internal probes (Fly,
# Railway, k8s) hit the container directly without traversing the TLS
# proxy, so they arrive as plain HTTP and would be 301-redirected,
# making the probe never see 200.
SECURE_REDIRECT_EXEMPT = [r"^healthz$", r"^readyz$"]

# X-Forwarded-Proto trust. ONLY enable when there's a TLS-terminating proxy
# (Caddy / nginx / managed load balancer) in front of gunicorn. Without one,
# any client on the open port can spoof X-Forwarded-Proto: https and Django
# will treat the request as secure — bypassing SECURE_SSL_REDIRECT and
# CSRF cookie protections.
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


# django-dbbackup (references/dbbackup.md) — VPS deploy + non-SQLite ⇒ default yes.
# No S3 was requested for this project, so backups land on a local path
# inside the container instead of the reference's S3Boto3Storage — mount
# that path onto a persistent volume in production.
# Wrapped in `if not DEBUG:` — the Dockerfile builder runs collectstatic
# with DJANGO_DEBUG=True, and dbbackup's app config touches storage
# settings at import time.
if not DEBUG:
    INSTALLED_APPS += ["dbbackup"]

    DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
    DBBACKUP_STORAGE_OPTIONS = {
        "location": env("DBBACKUP_STORAGE_DIR", default=str(BASE_DIR / "backups"))
    }

    DBBACKUP_CLEANUP_KEEP = 14  # daily backups retained
    DBBACKUP_CLEANUP_KEEP_MEDIA = 7
    DBBACKUP_FILENAME_TEMPLATE = "{databasename}-{servername}-{datetime}.{extension}"
