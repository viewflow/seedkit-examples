"""Settings for running the test suite."""

from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = "django-insecure-test-key"

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

AXES_ENABLED = False

TASKS = {
    "default": {
        "BACKEND": "django_tasks.backends.immediate.ImmediateBackend",
    },
}
