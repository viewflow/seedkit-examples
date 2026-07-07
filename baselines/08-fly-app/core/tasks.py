from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone


@shared_task
def purge_expired_access_logs():
    """GDPR: enforce DATA_RETENTION_DAYS on django-axes' IP/user access records."""
    from axes.models import AccessAttempt, AccessFailureLog, AccessLog

    cutoff = timezone.now() - timedelta(days=settings.DATA_RETENTION_DAYS)
    AccessAttempt.objects.filter(attempt_time__lt=cutoff).delete()
    AccessLog.objects.filter(attempt_time__lt=cutoff).delete()
    AccessFailureLog.objects.filter(attempt_time__lt=cutoff).delete()
