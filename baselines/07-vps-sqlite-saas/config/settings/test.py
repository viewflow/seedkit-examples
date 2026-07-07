from .base import *  # noqa: F403

DEBUG = False

SECRET_KEY = "test-secret-key"

DATABASES["default"]["NAME"] = ":memory:"  # noqa: F405
DATABASES["cache"]["NAME"] = ":memory:"  # noqa: F405

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Avoid needing a `createcachetable --database=cache` step just to run tests.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

AXES_ENABLED = False

TASKS = {
    "default": {
        "BACKEND": "django_tasks.backends.immediate.ImmediateBackend",
    },
}
