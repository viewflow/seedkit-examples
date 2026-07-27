from .base import *  # noqa: F403
from .base import LOGGING

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

CORS_ALLOW_ALL_ORIGINS = True

LOGGING["handlers"]["console"]["formatter"] = "console"
