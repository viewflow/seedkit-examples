"""Local development settings."""

from .base import *
from .base import INSTALLED_APPS, MIDDLEWARE, env

DEBUG = env.bool("DEBUG", default=True)

INSTALLED_APPS += [
    "django_extensions",
    "zeal",
]

# django-zeal: detect N+1 queries. Log instead of raising so third-party
# views (admin, silk) don't take the dev server down.
MIDDLEWARE = ["zeal.middleware.zeal_middleware", *MIDDLEWARE]
ZEAL_RAISE = False

# django-silk: profile every request; @silk_profile blocks show under /silk/.
SILKY_PYTHON_PROFILER = True

EMAIL_CONFIG = env.email_url("EMAIL_URL", default="consolemail://")
vars().update(EMAIL_CONFIG)

INTERNAL_IPS = ["127.0.0.1"]
