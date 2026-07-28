"""Production settings.

Deployment itself is out of scope for this scaffold — this module exists so the
"JSON logs in prod, pretty logs in dev" split has somewhere to live, and so the
obvious security switches are not left to be remembered later.
"""

from config.logging import build_logging_config, configure_structlog

from .base import *
from .base import csv_list, env

DEBUG = False
SECRET_KEY = env.str("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = csv_list(env.str("DJANGO_ALLOWED_HOSTS"))

LOG_JSON = True
LOG_LEVEL = env.str("DJANGO_LOG_LEVEL", default="INFO")
configure_structlog(json_logs=LOG_JSON)
LOGGING = build_logging_config(json_logs=LOG_JSON, level=LOG_LEVEL)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=60 * 60 * 24 * 7)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = csv_list(
    env.str("DJANGO_CSRF_TRUSTED_ORIGINS", default=""),
)

CORS_ALLOW_ALL_ORIGINS = False
