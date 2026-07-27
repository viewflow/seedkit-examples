from django.db.models.signals import post_save
from django.dispatch import receiver

from jobs.models import Job
from jobs.tasks import notify_new_job


@receiver(post_save, sender=Job)
def notify_new_job_on_save(sender, instance, created, **kwargs):
    if created:
        notify_new_job.delay(instance.pk)
