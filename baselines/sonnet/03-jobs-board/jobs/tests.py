from unittest import mock

from django.test import TestCase

from jobs.models import Job


class JobTests(TestCase):
    def test_saving_a_job_notifies_subscribers(self):
        with mock.patch("jobs.signals.notify_new_job.delay") as delay:
            job = Job.objects.create(
                title="Backend Engineer",
                company="Acme Inc",
                description="Build things.",
            )
        delay.assert_called_once_with(job.pk)
