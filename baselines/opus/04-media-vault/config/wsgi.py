"""WSGI entrypoint.

Kept for tooling that expects it, but this project serves WebSockets, so the
real entrypoint is ``config.asgi``.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

application = get_wsgi_application()
