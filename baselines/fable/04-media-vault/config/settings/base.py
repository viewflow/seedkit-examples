"""Base settings shared by every environment.

Environment-specific modules (``local``, and a future ``production``)
import everything from here and override what differs.
"""

# django-environ's stubs type every `default=` as NoValue, rejecting real
# default values; silence that single rule for this file.
# pyright: reportArgumentType=false

from pathlib import Path

import environ

from config.logging import build_logging, configure_structlog

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-dev-only-secret-key")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1", "[::1]", "0.0.0.0"],
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "channels",
    "corsheaders",
    "django_structlog",
    "django_rq",
    "django_tasks_rq",
    # Local
    "jobs",
    "api",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_structlog.middlewares.RequestMiddleware",
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
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database

DATABASES = {
    "default": env.db_url(
        "DATABASE_URL",
        default="postgres://media_vault:media_vault@127.0.0.1:5433/media_vault",
    ),
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Redis: channel layer + background task queue share one server

REDIS_URL = env("REDIS_URL", default="redis://127.0.0.1:6380/0")

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_URL]},
    },
}

# Django Tasks (django.tasks) backed by RQ

TASKS = {
    "default": {
        "BACKEND": "django_tasks_rq.RQBackend",
        "QUEUES": ["default"],
    },
}

RQ_QUEUES = {
    "default": {"URL": REDIS_URL},
}

# Make plain `manage.py rqworker default` use the django-tasks-rq job class.
RQ = {"JOB_CLASS": "django_tasks_rq.Job"}

# Auth

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalisation is disabled for this project

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True

# Static files & media storage (S3-compatible; MinIO in local Compose)

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": env("AWS_ACCESS_KEY_ID", default="minioadmin"),
            "secret_key": env("AWS_SECRET_ACCESS_KEY", default="minioadmin"),
            "bucket_name": env("AWS_STORAGE_BUCKET_NAME", default="media"),
            "endpoint_url": env("AWS_S3_ENDPOINT_URL", default="http://127.0.0.1:9002"),
            "region_name": env("AWS_S3_REGION_NAME", default="us-east-1"),
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Email

EMAIL_CONFIG = env.email_url("EMAIL_URL", default="consolemail://")
globals().update(EMAIL_CONFIG)

# CORS

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

# Logging: structlog everywhere, JSON by default (production-safe);
# the local settings switch to the pretty console renderer.

configure_structlog()
LOGGING = build_logging("json")
