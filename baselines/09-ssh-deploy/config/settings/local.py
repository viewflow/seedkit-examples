import structlog

from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(colors=True),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "plain_console",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
