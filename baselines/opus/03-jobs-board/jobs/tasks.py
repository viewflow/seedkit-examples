"""Background jobs for the board.

`send_job_posted_notification` is fired ad hoc when a posting goes live;
`send_daily_digest` is driven by Celery Beat (see CELERY_BEAT_SCHEDULE).
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


@shared_task
def send_job_posted_notification(job_id):
    """Email the poster to confirm their job is live."""
    from jobs.models import Job

    job = Job.objects.filter(pk=job_id).first()
    if job is None:
        logger.warning("send_job_posted_notification: job %s is gone", job_id)
        return "missing"

    send_mail(
        subject=_("Your job posting is live: %(title)s") % {"title": job.title},
        message=_("“%(title)s” at %(company)s is now visible on the board.")
        % {"title": job.title, "company": job.company},
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[job.apply_email],
    )
    logger.info("Notified %s about job %s", job.apply_email, job.pk)
    return "sent"


@shared_task
def send_daily_digest(days=1):
    """Mail every active subscriber the jobs published in the last `days`."""
    from jobs.models import DigestSubscriber, Job

    since = timezone.now() - timedelta(days=days)
    jobs = list(Job.objects.published_since(since))
    recipients = list(
        DigestSubscriber.objects.filter(is_active=True).values_list("email", flat=True)
    )

    if not jobs or not recipients:
        logger.info(
            "Daily digest skipped: %d job(s), %d subscriber(s)", len(jobs), len(recipients)
        )
        return {"jobs": len(jobs), "recipients": 0}

    lines = [f"- {job.title} @ {job.company} ({job.location or 'remote'})" for job in jobs]
    subject = _("Daily job digest: %(count)d new posting(s)") % {"count": len(jobs)}
    body = _("New on the board today:\n\n%(jobs)s") % {"jobs": "\n".join(lines)}

    # One message per subscriber — a shared recipient_list would expose every
    # subscriber's address to everyone else.
    for email in recipients:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
    logger.info("Daily digest: %d job(s) to %d subscriber(s)", len(jobs), len(recipients))
    return {"jobs": len(jobs), "recipients": len(recipients)}
