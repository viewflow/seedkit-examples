from django.db import models
from django.utils.translation import gettext_lazy as _


class Job(models.Model):
    title = models.CharField(_("title"), max_length=200)
    company = models.CharField(_("company"), max_length=200)
    description = models.TextField(_("description"))
    location = models.CharField(_("location"), max_length=200, blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("job")
        verbose_name_plural = _("jobs")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.company})"
