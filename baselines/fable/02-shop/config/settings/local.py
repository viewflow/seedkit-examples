"""Local development settings."""

from .base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INTERNAL_IPS = ["127.0.0.1"]

INSTALLED_APPS += ["django_browser_reload"]

MIDDLEWARE += ["django_browser_reload.middleware.BrowserReloadMiddleware"]

# Serve static files straight from the finders — no collectstatic needed in dev.
WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True

# Transactional email lands in the runserver console during development.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
