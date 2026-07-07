import uuid

import msgspec
from dmr import Body, Controller
from dmr.plugins.msgspec import MsgspecSerializer


class MediaUploadRequest(msgspec.Struct):
    filename: str
    size: int


class MediaUploadResponse(msgspec.Struct):
    uid: uuid.UUID
    filename: str


class MediaController(Controller[MsgspecSerializer]):
    async def post(
        self,
        parsed_body: Body[MediaUploadRequest],
    ) -> MediaUploadResponse:
        return MediaUploadResponse(
            uid=uuid.uuid4(),
            filename=parsed_body.filename,
        )
