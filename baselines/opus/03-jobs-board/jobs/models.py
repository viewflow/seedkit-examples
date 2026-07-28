from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class JobQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Job.Status.PUBLISHED)

    def published_since(self, since):
        return self.published().filter(published_at__gte=since)


class Job(models.Model):
    """A single job posting."""

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PUBLISHED = "published", _("Published")
        CLOSED = "closed", _("Closed")

    title = models.CharField(_("title"), max_length=200)
    company = models.CharField(_("company"), max_length=200)
    location = models.CharField(_("location"), max_length=200, blank=True)
    description = models.TextField(_("description"), blank=True)
    apply_email = models.EmailField(_("application email"))
    status = models.CharField(
        _("status"), max_length=16, choices=Status, default=Status.DRAFT
    )
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("posted by"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs",
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    published_at = models.DateTimeField(_("published at"), null=True, blank=True)

    objects = JobQuerySet.as_manager()

    class Meta:
        verbose_name = _("job")
        verbose_name_plural = _("jobs")
        ordering = ["-published_at", "-created_at"]
        indexes = [models.Index(fields=["status", "-published_at"])]

    def __str__(self):
        return f"{self.title} @ {self.company}"

    def get_absolute_url(self):
        return reverse("jobs:detail", args=[self.pk])

    def publish(self):
        """Mark the job live and stamp the publication time."""
        self.status = self.Status.PUBLISHED
        self.published_at = timezone.now()
        self.save(update_fields=["status", "published_at"])


class DigestSubscriber(models.Model):
    """Someone who wants the daily digest of new postings."""

    email = models.EmailField(_("email"), unique=True)
    is_active = models.BooleanField(_("active"), default=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("digest subscriber")
        verbose_name_plural = _("digest subscribers")
        ordering = ["email"]

    def __str__(self):
        return self.email
