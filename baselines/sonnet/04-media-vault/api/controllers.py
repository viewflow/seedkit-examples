import uuid

import msgspec
from dmr import Body, Controller
from dmr.plugins.msgspec import MsgspecSerializer


class MediaCreateRequest(msgspec.Struct):
    filename: str
    size: int


class MediaCreateResponse(msgspec.Struct):
    uid: uuid.UUID
    filename: str


class MediaController(Controller[MsgspecSerializer]):
    def post(self, parsed_body: Body[MediaCreateRequest]) -> MediaCreateResponse:
        return MediaCreateResponse(uid=uuid.uuid4(), filename=parsed_body.filename)
