"""Settings for the pytest suite."""
from .base import *  # noqa: F403

DEBUG = False

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

AXES_ENABLED = False

ACCOUNT_EMAIL_VERIFICATION = "none"
