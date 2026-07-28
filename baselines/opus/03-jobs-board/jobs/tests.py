from datetime import timedelta

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from jobs.models import DigestSubscriber, Job
from jobs.tasks import send_daily_digest, send_job_posted_notification


class JobModelTests(TestCase):
    def test_publish_sets_status_and_timestamp(self):
        job = Job.objects.create(
            title="Django Developer", company="Acme", apply_email="hr@acme.test"
        )
        self.assertIsNone(job.published_at)

        job.publish()
        job.refresh_from_db()

        self.assertEqual(job.status, Job.Status.PUBLISHED)
        self.assertIsNotNone(job.published_at)


class JobViewTests(TestCase):
    def test_list_shows_only_published_jobs(self):
        published = Job.objects.create(
            title="Published role",
            company="Acme",
            apply_email="hr@acme.test",
            status=Job.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        Job.objects.create(
            title="Draft role", company="Acme", apply_email="hr@acme.test"
        )

        response = self.client.get(reverse("jobs:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, published.title)
        self.assertNotContains(response, "Draft role")

    def test_detail_404s_for_unpublished_job(self):
        job = Job.objects.create(
            title="Draft role", company="Acme", apply_email="hr@acme.test"
        )
        response = self.client.get(reverse("jobs:detail", args=[job.pk]))
        self.assertEqual(response.status_code, 404)


class HealthEndpointTests(TestCase):
    def test_healthz(self):
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")

    def test_readyz(self):
        response = self.client.get("/readyz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ready")


class LoginPageTests(TestCase):
    def test_magic_link_login_page_renders(self):
        response = self.client.get(reverse("mailauth:login"))
        self.assertEqual(response.status_code, 200)


class TaskTests(TestCase):
    def test_notification_emails_the_poster(self):
        job = Job.objects.create(
            title="Django Developer", company="Acme", apply_email="hr@acme.test"
        )

        self.assertEqual(send_job_posted_notification(job.pk), "sent")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["hr@acme.test"])

    def test_notification_tolerates_a_deleted_job(self):
        self.assertEqual(send_job_posted_notification(12345), "missing")
        self.assertEqual(len(mail.outbox), 0)

    def test_digest_covers_recent_jobs_only(self):
        DigestSubscriber.objects.create(email="reader@example.test")
        Job.objects.create(
            title="Fresh role",
            company="Acme",
            apply_email="hr@acme.test",
            status=Job.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        Job.objects.create(
            title="Stale role",
            company="Acme",
            apply_email="hr@acme.test",
            status=Job.Status.PUBLISHED,
            published_at=timezone.now() - timedelta(days=5),
        )

        result = send_daily_digest()

        self.assertEqual(result, {"jobs": 1, "recipients": 1})
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Fresh role", mail.outbox[0].body)
        self.assertNotIn("Stale role", mail.outbox[0].body)

    def test_digest_skips_when_nothing_is_new(self):
        DigestSubscriber.objects.create(email="reader@example.test")
        self.assertEqual(send_daily_digest(), {"jobs": 0, "recipients": 0})
        self.assertEqual(len(mail.outbox), 0)


class CeleryAutodiscoveryTests(TestCase):
    def test_tasks_are_registered(self):
        from config import celery_app

        celery_app.loader.import_default_modules()
        self.assertIn("jobs.tasks.send_daily_digest", celery_app.tasks)
        self.assertIn("jobs.tasks.send_job_posted_notification", celery_app.tasks)

    def test_beat_schedule_points_at_a_real_task(self):
        from django.conf import settings

        from config import celery_app

        celery_app.loader.import_default_modules()
        for entry in settings.CELERY_BEAT_SCHEDULE.values():
            self.assertIn(entry["task"], celery_app.tasks)
