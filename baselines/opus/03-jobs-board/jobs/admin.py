from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _, ngettext

from jobs.models import DigestSubscriber, Job
from jobs.tasks import send_job_posted_notification


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "status", "published_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "company", "location")
    date_hierarchy = "created_at"
    actions = ("publish_jobs",)

    @admin.action(description=_("Publish selected jobs and notify the poster"))
    def publish_jobs(self, request, queryset):
        published = 0
        for job in queryset.exclude(status=Job.Status.PUBLISHED):
            job.publish()
            send_job_posted_notification.delay(job.pk)
            published += 1
        self.message_user(
            request,
            ngettext("%d job published.", "%d jobs published.", published) % published,
            messages.SUCCESS,
        )


@admin.register(DigestSubscriber)
class DigestSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("email",)
