from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Fast, insecure hasher for local dev/tests only.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
