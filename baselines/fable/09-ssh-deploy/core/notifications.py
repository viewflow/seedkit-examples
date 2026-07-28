import structlog
from django.conf import settings

logger = structlog.get_logger(__name__)


def send_transactional_email(subject: str, body: str, recipient: str) -> bool:
    """Send a transactional email, unless the project has email disabled.

    This project sends no transactional mail (TRANSACTIONAL_EMAIL_ENABLED is
    False), so callers get the skip path: nothing is sent and False is returned.
    """
    if not settings.TRANSACTIONAL_EMAIL_ENABLED:
        logger.info("transactional_email_skipped", subject=subject, recipient=recipient)
        return False

    from django.core.mail import send_mail

    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient])
    logger.info("transactional_email_sent", subject=subject, recipient=recipient)
    return True
