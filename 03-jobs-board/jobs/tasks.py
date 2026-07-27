import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_daily_digest():
    """Placeholder for the daily digest email — proves Celery Beat autodiscovery."""
    logger.info("send_daily_digest: no subscribers yet")
