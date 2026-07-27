from django.apps import AppConfig


class JobsConfig(AppConfig):
    name = "jobs"

    def ready(self) -> None:
        from jobs import tasks  # noqa: F401
