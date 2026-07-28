"""Background tasks executed by the Django Tasks database worker.

Run the worker with: ``manage.py db_worker``.
"""

import structlog
from django.tasks import task

logger = structlog.get_logger(__name__)


@task()
def sample_task(message: str) -> str:
    """A sample task: enqueue with ``sample_task.enqueue("hello")``."""
    logger.info("sample_task.run", message=message)
    return message
