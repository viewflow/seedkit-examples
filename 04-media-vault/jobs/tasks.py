# NOTE: django-tasks-rq 0.12.0 is built against the standalone `django-tasks`
# backport package (import path `django_tasks`), not Django 6's stdlib
# `django.tasks` module — even though Django 6 ships `django.tasks` in core.
# Importing from `django.tasks` here would create Task objects RQBackend
# doesn't recognise. See config/settings/base.py for the long version.
from django_tasks import task


@task
def process_upload(filename: str, size: int) -> str:
    """Placeholder background job — pretend to process a freshly uploaded
    media file. Real projects would fetch the object from S3, transcode /
    resize / scan it, then flip a status field."""
    return f"processed {filename} ({size} bytes)"
