"""Development settings: pretty console logs, permissive hosts, no HTTPS."""

from config.logging import build_logging_config, configure_structlog

from .base import *
from .base import env

DEBUG = env.bool("DJANGO_DEBUG", default=True)
LOG_JSON = env.bool("DJANGO_LOG_JSON", default=False)
LOG_LEVEL = env.str("DJANGO_LOG_LEVEL", default="DEBUG")
configure_structlog(json_logs=LOG_JSON)
LOGGING = build_logging_config(json_logs=LOG_JSON, level=LOG_LEVEL)

# Wide-open CORS is fine locally; production keeps an explicit allow-list.
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", default=True)

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
