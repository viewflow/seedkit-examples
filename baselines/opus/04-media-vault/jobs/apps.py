from django.apps import AppConfig


class JobsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jobs"

    def ready(self) -> None:
        # Importing the module registers the tasks so they can be enqueued by
        # dotted path from anywhere, including the worker process.
        from jobs import tasks  # noqa: F401
