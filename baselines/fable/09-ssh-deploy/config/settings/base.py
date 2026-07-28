"""Base settings shared by all environments."""

import os
from pathlib import Path

import structlog

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-key-do-not-use-in-production",
)

DEBUG = False

ALLOWED_HOSTS: list[str] = [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "django_structlog",
    "django_rq",
    "django_tasks_rq",
    "dbbackup",
    # Local
    "core",
    "jobs",
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
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.umami",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database ---------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "app"),
        "USER": os.environ.get("POSTGRES_USER", "app"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "app"),
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 60,
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Redis / background tasks ------------------------------------------------

REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")

RQ_QUEUES = {
    "default": {"URL": REDIS_URL},
}

# `manage.py rqworker` must use the django-tasks-rq job class to execute
# django.tasks-style Tasks pulled off the queue.
RQ = {"JOB_CLASS": "django_tasks_rq.Job"}

TASKS = {
    "default": {
        "BACKEND": "django_tasks_rq.RQBackend",
        "QUEUES": ["default"],
    }
}

# Caching (shared Redis instance, separate logical db) ---------------------

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("CACHE_REDIS_URL", "redis://127.0.0.1:6379/1"),
    }
}

# Auth --------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": f"django.contrib.auth.password_validation.{name}"}
    for name in [
        "UserAttributeSimilarityValidator",
        "MinimumLengthValidator",
        "CommonPasswordValidator",
        "NumericPasswordValidator",
    ]
]

# I18N is disabled: single-language project.

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True

# Static files -------------------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Email --------------------------------------------------------------------
# This project sends no transactional mail. core.notifications.send_transactional_email
# short-circuits unless TRANSACTIONAL_EMAIL_ENABLED is flipped on.

TRANSACTIONAL_EMAIL_ENABLED = False
EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@example.com"

# Content Security Policy (django-csp 4.x) ----------------------------------

UMAMI_HOST = os.environ.get("UMAMI_HOST", "").rstrip("/")
UMAMI_WEBSITE_ID = os.environ.get("UMAMI_WEBSITE_ID", "")

_csp_script_src = ["'self'"]
_csp_connect_src = ["'self'"]
if UMAMI_HOST:
    _csp_script_src.append(UMAMI_HOST)
    _csp_connect_src.append(UMAMI_HOST)

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "script-src": _csp_script_src,
        "connect-src": _csp_connect_src,
        "style-src": ["'self'", "'unsafe-inline'"],
        "img-src": ["'self'", "data:"],
        "font-src": ["'self'"],
        "object-src": ["'none'"],
        "base-uri": ["'self'"],
        "form-action": ["'self'"],
        "frame-ancestors": ["'none'"],
    }
}

# Database backups (django-dbbackup) ----------------------------------------

DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_STORAGE_OPTIONS = {
    "location": os.environ.get("DBBACKUP_DIR", str(BASE_DIR / "backups")),
}
DBBACKUP_CLEANUP_KEEP = 14
DBBACKUP_CLEANUP_KEEP_MEDIA = 14

# GDPR / data retention ------------------------------------------------------
# Retention defaults; enforced by scheduled jobs and dbbackup cleanup.

DATA_RETENTION_DAYS = int(os.environ.get("DATA_RETENTION_DAYS", "365"))
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # two weeks

# Logging (structlog: pretty console in dev, JSON in prod) -------------------

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

_foreign_pre_chain = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt="iso"),
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
            "foreign_pre_chain": _foreign_pre_chain,
        },
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
            "foreign_pre_chain": _foreign_pre_chain,
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "console"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django_structlog": {"level": "INFO"},
    },
}

DJANGO_STRUCTLOG_STATUS_4XX_LOG_LEVEL = 30  # WARNING
