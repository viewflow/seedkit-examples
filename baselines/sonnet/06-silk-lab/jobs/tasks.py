from django.core.mail import send_mail
from django_tasks import task


@task()
def send_welcome_email(recipient: str) -> None:
    send_mail(
        subject="Welcome to silk-lab",
        message="Your background task ran on the database backend.",
        from_email=None,
        recipient_list=[recipient],
    )
