"""REST API controllers (django-modern-rest)."""

import uuid

import msgspec
from dmr import Body, Controller
from dmr.plugins.msgspec import MsgspecSerializer


class MediaCreateModel(msgspec.Struct):
    """Request payload for registering an upload."""

    filename: str
    size: int


class MediaModel(msgspec.Struct):
    """Response payload: the registered media item."""

    uid: uuid.UUID
    filename: str


class MediaController(Controller[MsgspecSerializer]):
    async def post(self, parsed_body: Body[MediaCreateModel]) -> MediaModel:
        return MediaModel(uid=uuid.uuid4(), filename=parsed_body.filename)
