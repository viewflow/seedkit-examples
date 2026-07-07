from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Console backend regardless of EMAIL_URL while developing locally.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Mandatory verification is annoying to click through during local dev; the
# console backend prints the link so it's still exercised, but relax axes
# lockouts so a few bad logins while testing don't lock you out for an hour.
AXES_ENABLED = False
