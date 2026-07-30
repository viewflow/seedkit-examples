from celery import shared_task


@shared_task
def send_daily_digest():
    """Sample periodic task — proves Celery Beat autodiscovery end to end."""
    return "daily digest sent"
