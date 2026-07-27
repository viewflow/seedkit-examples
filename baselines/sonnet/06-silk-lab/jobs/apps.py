from django.apps import AppConfig


class JobsConfig(AppConfig):
    name = 'jobs'

    def ready(self):
        from jobs import tasks  # noqa: F401
