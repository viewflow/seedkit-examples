import structlog
from django.contrib.sessions.models import Session
from django.utils import timezone
from django_tasks import task

logger = structlog.get_logger(__name__)


@task()
def cleanup_expired_sessions() -> int:
    """Delete expired sessions; sample background task for the RQ worker."""
    deleted, _ = Session.objects.filter(expire_date__lt=timezone.now()).delete()
    logger.info("expired_sessions_cleaned", deleted=deleted)
    return deleted
