"""Settings shared by every environment.

Environment-specific modules (``local``, ``production``) import ``*`` from
here and override what they need.
"""

from pathlib import Path

import environ

from config.logging import build_logging_config, configure_structlog

# config/settings/base.py -> config/settings -> config -> <project root>
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")


def csv_list(value: str) -> list[str]:
    """Split a comma-separated env value into a clean list.

    Preferred over ``env.list(..., default=[...])``: django-environ leaves the
    ``default`` argument of its container getters unannotated, which every type
    checker reads as "must be the NOTSET sentinel".
    """
    return [item.strip() for item in value.split(",") if item.strip()]


SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="insecure-change-me")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = csv_list(
    env.str(
        "DJANGO_ALLOWED_HOSTS",
        default="localhost,127.0.0.1,0.0.0.0,[::1]",
    ),
)


# Applications
# ------------------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "channels",
    "corsheaders",
    "django_rq",
    "django_tasks",
    "django_tasks_rq",
    "storages",
    # Local
    "api",
    "jobs",
]

MIDDLEWARE = [
    "config.logging.RequestIDMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
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
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# Database
# ------------------------------------------------------------------------------

DATABASES = {
    "default": env.db_url_config(
        env.str(
            "DATABASE_URL",
            default="postgres://postgres:postgres@127.0.0.1:5432/media_vault",
        ),
    ),
}
# Deliberately NOT setting ATOMIC_REQUESTS: Django refuses to wrap async views
# in a transaction, and this project's controllers/consumers are async. Wrap
# writes in an explicit `transaction.atomic()` instead.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Redis / cache / channel layer / queues
# ------------------------------------------------------------------------------

REDIS_URL = env.str("REDIS_URL", default="redis://127.0.0.1:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    },
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_URL]},
    },
}

RQ_QUEUES = {
    "default": {
        "URL": REDIS_URL,
        "DEFAULT_TIMEOUT": 600,
    },
}

# `django-tasks-rq` needs its own RQ ``Job`` subclass. Setting it here means a
# plain `manage.py rqworker default` picks it up without `--job-class`.
RQ = {"JOB_CLASS": "django_tasks_rq.Job"}

TASKS = {
    "default": {
        "BACKEND": "django_tasks_rq.RQBackend",
        "QUEUES": ["default"],
    },
}


# Password validation
# ------------------------------------------------------------------------------

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


# I18N / time
# ------------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True


# Static & media storage
# ------------------------------------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME", default="media")
AWS_S3_REGION_NAME = env.str("AWS_S3_REGION_NAME", default="us-east-1")
# Empty means "real AWS"; MinIO sets this to http://127.0.0.1:9000.
AWS_S3_ENDPOINT_URL = env.str("AWS_S3_ENDPOINT_URL", default="") or None
AWS_S3_ADDRESSING_STYLE = env.str("AWS_S3_ADDRESSING_STYLE", default="path")
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = True
AWS_DEFAULT_ACL = None

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
            "region_name": AWS_S3_REGION_NAME,
            "addressing_style": AWS_S3_ADDRESSING_STYLE,
            "file_overwrite": AWS_S3_FILE_OVERWRITE,
            "default_acl": AWS_DEFAULT_ACL,
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


# Email
# ------------------------------------------------------------------------------

# Yields EMAIL_BACKEND/EMAIL_HOST/... — splat it into the module namespace.
globals().update(
    env.email_url_config(env.str("EMAIL_URL", default="consolemail://")),
)
DEFAULT_FROM_EMAIL = env.str(
    "DEFAULT_FROM_EMAIL",
    default="media-vault <noreply@localhost>",
)


# CORS
# ------------------------------------------------------------------------------

CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", default=False)
CORS_ALLOWED_ORIGINS = csv_list(env.str("CORS_ALLOWED_ORIGINS", default=""))
CORS_ALLOW_CREDENTIALS = env.bool("CORS_ALLOW_CREDENTIALS", default=True)
CORS_URLS_REGEX = r"^/(api|ws)/.*$"


# Logging (structlog) — see config/logging.py
# ------------------------------------------------------------------------------

LOG_LEVEL = env.str("DJANGO_LOG_LEVEL", default="INFO")
LOG_JSON = env.bool("DJANGO_LOG_JSON", default=not DEBUG)

# Environment modules that change LOG_JSON/LOG_LEVEL must re-run these two
# lines; `LOGGING` is a plain dict, so it does not pick up later overrides.
configure_structlog(json_logs=LOG_JSON)
LOGGING = build_logging_config(json_logs=LOG_JSON, level=LOG_LEVEL)
