"""Settings for the django-bolt API process.

Fast path: strips the session/CSRF/template stack that the Rust HTTP layer
never uses. `runbolt` runs with DJANGO_SETTINGS_MODULE=config.settings.bolt;
`runserver`/`gunicorn` keep using local/production.
"""

from .base import *
from .base import INSTALLED_APPS, MIDDLEWARE

_STRIPPED_APPS = {
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
}

_STRIPPED_MIDDLEWARE = {
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
}

INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in _STRIPPED_APPS]
MIDDLEWARE = [mw for mw in MIDDLEWARE if mw not in _STRIPPED_MIDDLEWARE]

TEMPLATES = []

ROOT_URLCONF = "config.urls_bolt"
