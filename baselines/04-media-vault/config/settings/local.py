"""Local development settings.

DEBUG and the structlog renderer (pretty console vs. JSON) are controlled by
``DJANGO_DEBUG`` in ``.env`` — see base.py. This module only adds local-only
fallbacks so the project runs out of the box against `.env.example` values.
"""

from .base import *  # noqa: F403
from .base import env

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS',
    default=['http://localhost:3000'],
)
