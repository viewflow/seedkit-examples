import os

from celery import Celery

# A worker booted without DJANGO_SETTINGS_MODULE set should run with prod
# hardening; the host dev shell sets DJANGO_SETTINGS_MODULE=config.settings.local
# to override.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
