import structlog
from django_tasks import task

logger = structlog.get_logger(__name__)


@task
def process_media(uid: str, filename: str) -> None:
    """Sample background task: stand-in for post-upload media processing."""
    logger.info("processing_media", uid=uid, filename=filename)
