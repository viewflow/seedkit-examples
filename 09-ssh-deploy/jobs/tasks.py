import structlog
from django.tasks import task

logger = structlog.get_logger(__name__)


@task
def log_greeting(name: str) -> None:
    logger.info("greeting_sent", name=name)
