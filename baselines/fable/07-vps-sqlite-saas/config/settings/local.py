"""Local development settings."""

from .base import *  # noqa: F403
from .base import env

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Keep axes out of the way while developing.
AXES_ENABLED = env.bool("AXES_ENABLED", default=True)

# Plain static file serving, no manifest, so runserver works without collectstatic.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

WHITENOISE_USE_FINDERS = True
