"""Background tasks, executed by RQ workers.

Run a worker with:
    uv run manage.py rqworker default
"""

import structlog
from django.tasks import task

logger = structlog.get_logger(__name__)


@task
def process_media(filename: str) -> str:
    """Sample task: pretend to process an uploaded media file."""
    logger.info("media_processing_started", filename=filename)
    result = f"processed:{filename}"
    logger.info("media_processing_finished", filename=filename, result=result)
    return result
