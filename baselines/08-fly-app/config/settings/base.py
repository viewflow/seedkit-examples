"""Base Django settings shared by every environment."""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="django-insecure-change-me-in-production")

DEBUG = env.bool("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])  # pyright: ignore[reportArgumentType]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "storages",
    "mailauth",
    "axes",
    "anymail",
    "django_bolt",
    # local
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
    "csp.middleware.CSPMiddleware",
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
ASGI_APPLICATION = "config.asgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://postgres:postgres@127.0.0.1:5432/fly_app",  # pyright: ignore[reportArgumentType]
    ),
}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DJANGO_CONN_MAX_AGE", default=60)


# Cache / Redis

REDIS_URL = env.str("REDIS_URL", default="redis://127.0.0.1:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}


# Authentication

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "mailauth.backends.MailAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_URL = "mailauth:login"
LOGIN_REDIRECT_URL = "/"
LOGIN_URL_TIMEOUT = 60 * 15
LOGIN_TOKEN_SINGLE_USE = True

AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # hours
AXES_LOCKOUT_PARAMETERS = ["ip_address", "username"]
AXES_RESET_ON_SUCCESS = True

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Object storage (S3-compatible: MinIO locally, real S3 in prod)

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME", default="fly-app")
AWS_S3_REGION_NAME = env.str("AWS_S3_REGION_NAME", default="us-east-1")
AWS_S3_ENDPOINT_URL = env.str("AWS_S3_ENDPOINT_URL", default="") or None
AWS_S3_CUSTOM_DOMAIN = env.str("AWS_S3_CUSTOM_DOMAIN", default="") or None
AWS_S3_ADDRESSING_STYLE = "path"
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = env.bool("AWS_QUERYSTRING_AUTH", default=False)


# Celery

CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", default=REDIS_URL)
CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", default=REDIS_URL)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_BEAT_SCHEDULE = {
    "purge-expired-access-logs": {
        "task": "core.tasks.purge_expired_access_logs",
        "schedule": 60 * 60 * 24,  # daily
    },
}


# Email (Anymail / Postmark). See config/settings/production.py for the
# non-DEBUG Postmark backend switch-over.

EMAIL_BACKEND = env.str("DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default="no-reply@example.com")
SERVER_EMAIL = env.str("SERVER_EMAIL", default="server-errors@example.com")

ANYMAIL = {
    "POSTMARK_SERVER_TOKEN": env.str("POSTMARK_SERVER_TOKEN", default=""),
    "WEBHOOK_SECRET": env.str("ANYMAIL_WEBHOOK_SECRET", default=""),
}


# Analytics (GA4)

GA4_MEASUREMENT_ID = env.str("GA4_MEASUREMENT_ID", default="")


# Sentry-compatible error reporting (GlitchTip)

GLITCHTIP_DSN = env.str("GLITCHTIP_DSN", default="")


# GDPR: how long we retain access-log / audit data, in days.
DATA_RETENTION_DAYS = env.int("DATA_RETENTION_DAYS", default=30)
