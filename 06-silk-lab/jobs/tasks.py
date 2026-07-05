import logging

from django_tasks import task

logger = logging.getLogger(__name__)


@task()
def send_welcome_email(recipient: str) -> None:
    from django.core.mail import send_mail

    send_mail(
        subject="Welcome",
        message=f"Thanks for signing up, {recipient}!",
        from_email=None,
        recipient_list=[recipient],
    )
    logger.info("Sent welcome email to %s", recipient)
