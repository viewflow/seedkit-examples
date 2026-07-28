"""Tests for background tasks and the WebSocket layer."""

import json
from unittest import mock

# `channels.testing` pulls in its live-server helper, which imports daphne —
# hence daphne being a dev dependency even though we serve with uvicorn.
from channels.testing import WebsocketCommunicator
from django.test import TestCase, TransactionTestCase, override_settings

from config.asgi import application
from jobs.tasks import process_media


class ProcessMediaTaskTests(TestCase):
    def test_task_runs_and_returns_the_uid(self) -> None:
        with mock.patch("jobs.tasks._broadcast") as broadcast:
            result = process_media.call(
                media_uid="abc123",
                filename="a.png",
                size=42,
            )

        self.assertEqual(result, "abc123")
        self.assertEqual(
            [call.kwargs["status"] for call in broadcast.call_args_list],
            ["processing", "done"],
        )


@override_settings(
    CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}},
)
class EchoConsumerTests(TransactionTestCase):
    async def test_echoes_json_back(self) -> None:
        communicator = WebsocketCommunicator(
            application,
            "/ws/echo/",
            headers=[(b"origin", b"http://localhost"), (b"host", b"localhost")],
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_to(text_data=json.dumps({"text": "ping"}))
        response = await communicator.receive_from()

        self.assertEqual(json.loads(response), {"text": "ping"})
        await communicator.disconnect()
