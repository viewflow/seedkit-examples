from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail


@shared_task
def ping():
    """Trivial task to prove the Celery worker and autodiscovery work."""
    return "pong"


@shared_task
def send_job_notification(email, job_title):
    """Notify a candidate by email about a newly posted job."""
    send_mail(
        subject=f"New job posted: {job_title}",
        message=f"A new job matching your profile was posted: {job_title}.",
        from_email=None,
        recipient_list=[email],
    )


@shared_task
def send_daily_digest():
    """Send the daily digest to all active users. Scheduled via Celery Beat."""
    emails = (
        get_user_model()
        .objects.filter(is_active=True)
        .exclude(email="")
        .values_list("email", flat=True)
    )
    for email in emails:
        send_mail(
            subject="Your daily jobs digest",
            message="Here are the latest jobs posted in the last 24 hours.",
            from_email=None,
            recipient_list=[email],
        )
    return len(emails)
