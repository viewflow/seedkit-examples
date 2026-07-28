"""API controllers."""

import uuid

import structlog
from dmr import Body, Controller
from dmr.plugins.msgspec import MsgspecSerializer

from api.schemas import MediaCreateRequest, MediaCreateResponse
from jobs.tasks import process_media

logger = structlog.get_logger(__name__)


class MediaController(Controller[MsgspecSerializer]):
    """Register an upload and hand back the id clients subscribe with."""

    async def post(
        self,
        parsed_body: Body[MediaCreateRequest],
    ) -> MediaCreateResponse:
        """Accept upload metadata and queue the processing job."""
        uid = uuid.uuid4()
        await process_media.aenqueue(
            media_uid=str(uid),
            filename=parsed_body.filename,
            size=parsed_body.size,
        )
        await logger.ainfo(
            "media.registered",
            media_uid=str(uid),
            filename=parsed_body.filename,
            size=parsed_body.size,
        )
        return MediaCreateResponse(uid=uid, filename=parsed_body.filename)
