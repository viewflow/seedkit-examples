"""API tests. Run with ``uv run manage.py test``."""

import json
import uuid

from django.test import TestCase, override_settings
from django.urls import reverse
from django_tasks import default_task_backend

# Records enqueued tasks instead of pushing them to Redis, so the tests do not
# need a running worker.
_DUMMY_TASKS = {"default": {"BACKEND": "django_tasks.backends.dummy.DummyBackend"}}


@override_settings(TASKS=_DUMMY_TASKS)
class MediaControllerTests(TestCase):
    """POST /api/media/ contract."""

    url = "/api/media/"

    def setUp(self) -> None:
        # The backend instance is shared for the whole class, so its recorded
        # results have to be reset between tests.
        default_task_backend.results.clear()  # type: ignore[attr-defined]

    def test_url_is_reversible(self) -> None:
        self.assertEqual(reverse("api:media"), self.url)

    def test_accepts_valid_payload(self) -> None:
        response = self.client.post(
            self.url,
            data=json.dumps({"filename": "a.png", "size": 42}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        body = json.loads(response.content)
        self.assertEqual(body["filename"], "a.png")
        uuid.UUID(body["uid"])  # raises if it is not a well-formed uuid

    def test_queues_the_processing_task(self) -> None:
        self.client.post(
            self.url,
            data=json.dumps({"filename": "a.png", "size": 42}),
            content_type="application/json",
        )

        results = default_task_backend.results  # type: ignore[attr-defined]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].task.name, "process_media")
        self.assertEqual(results[0].kwargs["filename"], "a.png")

    def test_rejects_payload_missing_size(self) -> None:
        response = self.client.post(
            self.url,
            data=json.dumps({"filename": "a.png"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_rejects_wrong_type_for_size(self) -> None:
        response = self.client.post(
            self.url,
            data=json.dumps({"filename": "a.png", "size": "big"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)


class HealthEndpointTests(TestCase):
    def test_healthz_is_dependency_free(self) -> None:
        response = self.client.get("/healthz")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")
