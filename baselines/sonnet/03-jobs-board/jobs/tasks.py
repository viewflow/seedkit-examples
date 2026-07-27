import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_application_notification(job_title):
    """Notify subscribers that a new job was posted (stub)."""
    logger.info("Notification sent for job posting: %s", job_title)


@shared_task
def send_daily_digest():
    """Compile and email the daily digest of new job postings (stub)."""
    logger.info("Daily digest sent.")
