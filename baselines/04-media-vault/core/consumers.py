from channels.generic.websocket import AsyncJsonWebsocketConsumer


class EchoConsumer(AsyncJsonWebsocketConsumer):
    """Accepts a WebSocket connection and echoes back any JSON it receives."""

    async def connect(self):
        await self.accept()

    async def receive_json(self, content, **kwargs):
        await self.send_json(content)
