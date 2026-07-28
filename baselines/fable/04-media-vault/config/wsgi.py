"""WSGI config. The project is served over ASGI (see ``asgi.py``); this
entrypoint exists for WSGI-only tooling."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

application = get_wsgi_application()
