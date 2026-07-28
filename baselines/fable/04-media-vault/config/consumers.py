"""Project-level WebSocket consumers."""

from typing import Any

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class EchoConsumer(AsyncJsonWebsocketConsumer):
    """Echo every received JSON message back to the sender."""

    async def receive_json(self, content: Any, **kwargs: Any) -> None:
        await self.send_json(content)
