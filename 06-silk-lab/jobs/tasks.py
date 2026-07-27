from django.conf import settings
from django.core.mail import send_mail
from django_tasks import task


@task
def send_welcome_email(recipient: str) -> None:
    send_mail(
        subject="Welcome",
        message="Thanks for signing up.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
    )
