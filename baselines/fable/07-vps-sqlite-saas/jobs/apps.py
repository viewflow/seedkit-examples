from django.apps import AppConfig


class JobsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jobs"

    def ready(self) -> None:
        # Import tasks so they register with the task backend on startup.
        from jobs import tasks  # noqa: F401
