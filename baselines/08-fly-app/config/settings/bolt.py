"""Settings for the `manage.py runbolt` process: a lean, API-only stack."""

from .base import *  # noqa: F403
from .base import INSTALLED_APPS, MIDDLEWARE

INSTALLED_APPS = [
    app
    for app in INSTALLED_APPS
    if app
    not in {
        "django.contrib.admin",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    }
]

MIDDLEWARE = [
    middleware
    for middleware in MIDDLEWARE
    if middleware
    not in {
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
    }
]

TEMPLATES = []
ROOT_URLCONF = "config.urls_bolt"
