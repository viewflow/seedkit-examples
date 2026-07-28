from celery import shared_task
from django.core.management import call_command


@shared_task
def ping() -> str:
    """Trivial task to verify the worker wiring."""
    return "pong"


@shared_task
def purge_expired_sessions() -> None:
    """GDPR retention: drop expired session rows (scheduled daily)."""
    call_command("clearsessions")
