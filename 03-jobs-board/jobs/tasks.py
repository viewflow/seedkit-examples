import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def add(x, y):
    return x + y


@shared_task
def ping():
    """Beat-scheduled — proves Celery Beat + autodiscovery both work end to end."""
    logger.info("pong")
    return "pong"
