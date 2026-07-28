"""WebSocket consumers.

``EchoConsumer`` is the round-trip smoke test for the channels stack: connect,
send JSON, get the same JSON back.
"""

from typing import Any

import structlog
from channels.generic.websocket import AsyncJsonWebsocketConsumer

logger = structlog.get_logger(__name__)


class EchoConsumer(AsyncJsonWebsocketConsumer):
    """Echo every received JSON payload straight back to the sender."""

    async def connect(self) -> None:
        await self.accept()
        await logger.adebug("websocket.connected", path=self.scope.get("path"))

    async def receive_json(self, content: Any, **kwargs: Any) -> None:
        await logger.adebug("websocket.echo", payload=content)
        await self.send_json(content)

    async def disconnect(self, code: int) -> None:
        await logger.adebug("websocket.disconnected", code=code)
