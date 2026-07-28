from django.apps import AppConfig


class JobsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jobs"

    def ready(self) -> None:
        # Import tasks so they are registered when the app loads.
        from jobs import tasks  # noqa: F401
