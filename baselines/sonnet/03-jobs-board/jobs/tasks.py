import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def notify_new_job(job_id):
    """Notify subscribers that a new job was posted."""
    logger.info("New job posted: %s", job_id)


@shared_task
def send_daily_digest():
    """Email everyone who opted in a digest of new job postings."""
    logger.info("Sending daily digest emails")
