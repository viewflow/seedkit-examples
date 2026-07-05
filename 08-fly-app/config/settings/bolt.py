from .base import *
from .base import INSTALLED_APPS, MIDDLEWARE

# Auth happens in Rust (JWT / API key) — Django auth middleware adds no value.
# Sessions / messages / CSRF only apply to browser flows that don't reach bolt.
_DROP_MIDDLEWARE = {
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
}
MIDDLEWARE = [m for m in MIDDLEWARE if m not in _DROP_MIDDLEWARE]

# Admin / sessions / messages / staticfiles aren't served by bolt.
_DROP_APPS = {
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
}
INSTALLED_APPS = [a for a in INSTALLED_APPS if a not in _DROP_APPS]

# No HTML rendering on the API path.
TEMPLATES = []

ROOT_URLCONF = "config.urls_bolt"  # API-only URLConf, no admin / accounts
