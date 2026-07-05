import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_job_notification(job_id):
    logger.info("Notifying subscribers about job %s", job_id)


@shared_task
def send_daily_digest():
    logger.info("Sending daily job digest")
