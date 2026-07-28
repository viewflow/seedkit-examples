"""Local development settings."""

from config.logging import build_logging

from .base import *  # noqa: F403
from .base import env

DEBUG = env.bool("DEBUG", default=True)

CORS_ALLOW_ALL_ORIGINS = True

# Pretty, human-readable logs in development.
LOGGING = build_logging("console")
