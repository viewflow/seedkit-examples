"""Celery application for the jobs board."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Every CELERY_-prefixed Django setting becomes a Celery setting.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Pick up tasks.py from every app in INSTALLED_APPS.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Print the request — handy for checking that a worker is alive."""
    print(f"Request: {self.request!r}")
