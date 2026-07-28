"""Settings shared by every environment."""

from datetime import timedelta
from pathlib import Path
from typing import Any

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Typed as Any: django-environ's stubs declare `default: NoValue`, which makes
# every `env(..., default=...)` call a false positive under pyright.
env: Any = environ.Env(DEBUG=(bool, False))

# Load a local .env if present (never committed).
environ.Env.read_env(BASE_DIR / ".env")

DEBUG = env("DEBUG")

SECRET_KEY = env("SECRET_KEY", default="django-insecure-dev-only-key")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    # Third-party
    "django_bolt",
    "anymail",
    "axes",
    "mailauth",
    "storages",
    # Local
    "core",
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.analytics",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": env.db(
        "DATABASE_URL", default="postgres://postgres:postgres@127.0.0.1:5432/fly_app"
    ),
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REDIS_URL = env("REDIS_URL", default="redis://127.0.0.1:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    },
}

# Authentication — passwordless magic links (django-mail-auth) guarded by django-axes.
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
    "mailauth.backends.MailAuthBackend",
]

LOGIN_URL = "mailauth:login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL_TIMEOUT = 60 * 15

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# django-axes
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(hours=1)
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True

# Static files (whitenoise) and media (S3-compatible: MinIO locally, S3 in prod).
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"

STORAGES = {
    "default": {"BACKEND": "storages.backends.s3.S3Storage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="minioadmin")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="minioadmin")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="fly-app-media")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="us-east-1")
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default="http://127.0.0.1:9000")
AWS_S3_FILE_OVERWRITE = False

# Email — console backend by default; production switches to anymail/Postmark.
globals().update(env.email_url("EMAIL_URL", default="consolemail://"))
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@example.com")
SERVER_EMAIL = env("SERVER_EMAIL", default="server@example.com")

ANYMAIL: dict[str, str] = {
    "POSTMARK_SERVER_TOKEN": env("POSTMARK_SERVER_TOKEN", default=""),
}
_anymail_webhook_secret = env("ANYMAIL_WEBHOOK_SECRET", default="")
if _anymail_webhook_secret:
    ANYMAIL["WEBHOOK_SECRET"] = _anymail_webhook_secret

# Celery
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TASK_TIME_LIMIT = 10 * 60
CELERY_BEAT_SCHEDULE = {
    # GDPR retention: drop expired sessions daily.
    "purge-expired-sessions": {
        "task": "core.tasks.purge_expired_sessions",
        "schedule": timedelta(days=1),
    },
}

# Google Analytics 4 — rendered by templates only when a measurement id is set.
GA4_MEASUREMENT_ID = env("GA4_MEASUREMENT_ID", default="")

# GDPR retention defaults
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # two weeks
DATA_RETENTION_DAYS = env.int("DATA_RETENTION_DAYS", default=365)
