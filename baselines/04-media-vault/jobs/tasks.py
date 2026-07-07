import structlog
from django_tasks import task

logger = structlog.get_logger(__name__)


@task
def process_media(filename: str, size: int) -> str:
    """Sample background job: pretend to process an uploaded media file."""
    logger.info('processing_media', filename=filename, size=size)
    return f'processed {filename} ({size} bytes)'
