"""
Base Django settings for config project, shared by local.py and production.py.
"""

import sys
from pathlib import Path

import environ
import structlog

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="django-insecure-change-me-in-production")

ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1"],  # pyright: ignore[reportArgumentType]
)

DEBUG = False

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # third-party
    "allauth",
    "allauth.account",
    "allauth.mfa",
    "axes",
    "csp",
    "django_structlog",
    "django_tasks",
    "django_tasks_db",
    # local
    "users",
    "jobs",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "axes.middleware.AxesMiddleware",
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
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": env.str("DJANGO_DB_PATH", default=str(BASE_DIR / "db.sqlite3")),
        "OPTIONS": {
            "init_command": (
                "PRAGMA journal_mode=WAL;PRAGMA synchronous=NORMAL;PRAGMA busy_timeout=5000;"
            ),
            "transaction_mode": "IMMEDIATE",
        },
    },
    "cache": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": env.str("DJANGO_CACHE_DB_PATH", default=str(BASE_DIR / "cache.sqlite3")),
        "OPTIONS": {
            "init_command": (
                "PRAGMA journal_mode=WAL;PRAGMA synchronous=NORMAL;PRAGMA busy_timeout=5000;"
            ),
        },
    },
}

DATABASE_ROUTERS = ["config.routers.CacheRouter"]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
    },
}

# django-tasks
# https://github.com/RealOrangeOne/django-tasks

TASKS = {
    "default": {
        "BACKEND": "django_tasks_db.backend.DatabaseBackend",
    },
}

# Custom user model

AUTH_USER_MODEL = "users.User"

SITE_ID = 1

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesBackend",
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
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

# Media files (user uploads) - served from a volume on the VPS host

MEDIA_URL = "media/"
MEDIA_ROOT = env.str("DJANGO_MEDIA_ROOT", default=str(BASE_DIR / "media"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# django-allauth
# https://docs.allauth.org/en/latest/account/configuration.html

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_RATE_LIMITS = {
    "login_failed": "5/5m/ip,5/5m/key",
}

MFA_SUPPORTED_TYPES = ["totp", "recovery_codes", "webauthn"]

# django-axes
# https://django-axes.readthedocs.io/

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # hours
AXES_LOCKOUT_PARAMETERS = ["username", "ip_address"]
AXES_RESET_ON_SUCCESS = True

# Email
# https://docs.djangoproject.com/en/5.1/topics/email/

EMAIL_CONFIG = env.email_url(
    "EMAIL_URL",
    default="consolemail://",  # pyright: ignore[reportArgumentType]
)
vars().update(EMAIL_CONFIG)

DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default="webmaster@localhost")
SERVER_EMAIL = env.str("SERVER_EMAIL", default="root@localhost")

ADMINS = [
    tuple(admin.split(":"))
    for admin in env.list("DJANGO_ADMINS", default=[])  # pyright: ignore[reportArgumentType]
]

# structlog
# https://django-structlog.readthedocs.io/

DJANGO_STRUCTLOG_ACTION_ON_TOP_LEVEL_EXCEPTION = "LOG_AND_RAISE"

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.dict_tracebacks,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processors": [
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.JSONRenderer(),
            ],
        },
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processors": [
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.dev.ConsoleRenderer(),
            ],
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "plain_console",
            "stream": sys.stdout,
        },
        "json": {
            "class": "logging.StreamHandler",
            "formatter": "json_formatter",
            "stream": sys.stdout,
        },
    },
    "loggers": {
        "django_structlog": {"handlers": ["console"], "level": "INFO"},
        "django": {"handlers": ["console"], "level": "INFO"},
        "": {"handlers": ["console"], "level": "INFO"},
    },
}
