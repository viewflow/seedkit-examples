from django.apps import AppConfig


class JobsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jobs"

    def ready(self):
        # Import tasks so @task callables register on app startup.
        from . import tasks  # noqa: F401
