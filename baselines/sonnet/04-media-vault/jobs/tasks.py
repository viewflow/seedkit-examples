import structlog
from django_tasks import task

logger = structlog.get_logger(__name__)


@task()
def process_media_upload(filename: str, size: int) -> str:
    """Placeholder background job for a media file that just landed in S3."""
    logger.info("processing_media_upload", filename=filename, size=size)
    return f"processed {filename} ({size} bytes)"
