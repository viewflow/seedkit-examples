import structlog
from django_tasks import task

logger = structlog.get_logger(__name__)


@task
def send_welcome_email(user_id: int) -> None:
    """Sample background task, enqueued via the Database task backend."""
    from users.models import User

    user = User.objects.get(pk=user_id)
    logger.info("welcome_email.sent", user_id=user.pk, email=user.email)
