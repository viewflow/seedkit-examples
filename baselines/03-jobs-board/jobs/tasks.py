import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_application_notification(applicant_email):
    logger.info("Notifying %s about their job application", applicant_email)


@shared_task
def send_daily_digest():
    logger.info("Sending daily job digest email")
