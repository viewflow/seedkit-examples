"""Local development settings."""

from config.settings._logging import build_logging_config
from config.settings.base import *  # noqa: F403
from config.settings.base import env

DEBUG = env.bool("DJANGO_DEBUG", default=True)

ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"],  # pyright: ignore[reportArgumentType]
)

CORS_ALLOW_ALL_ORIGINS = True

LOGGING = build_logging_config(json_logs=False)
