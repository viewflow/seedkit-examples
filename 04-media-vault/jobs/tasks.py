import structlog
from django_tasks import task

logger = structlog.get_logger(__name__)


@task
def process_media(filename: str, size: int) -> None:
    logger.info("processing_media", filename=filename, size=size)
