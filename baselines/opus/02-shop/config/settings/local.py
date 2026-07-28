"""Local development settings."""

# ruff: noqa: F403, F405
from .base import *

DEBUG = env.bool("DJANGO_DEBUG", default=True)

SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="django-insecure-local-only-key")

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "[::1]", "testserver"]

INTERNAL_IPS = ["127.0.0.1"]

# E-mail goes to the console instead of a real SMTP server.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Serve static files straight from disk; no manifest, no compression.
STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
}

# Let WhiteNoise use the staticfiles finders so it works without collectstatic.
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

# Faster password hashing keeps the test suite snappy.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# django-browser-reload: refresh the page whenever a template or CSS file changes.
INSTALLED_APPS = [*INSTALLED_APPS, "django_browser_reload"]
MIDDLEWARE = [*MIDDLEWARE, "django_browser_reload.middleware.BrowserReloadMiddleware"]
