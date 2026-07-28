"""Background tasks.

Enqueued through Django Tasks (``django_tasks``) and executed by an RQ worker:

    uv run manage.py rqworker default
"""

import structlog
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django_tasks import task

logger = structlog.get_logger(__name__)


@task()
def process_media(*, media_uid: str, filename: str, size: int) -> str:
    """Pretend to transcode an upload, then tell subscribers it is done.

    The real work would pull the object out of S3 and write derivatives back;
    what matters for the scaffold is the shape: queued off the request path,
    reporting progress over the channel layer.
    """
    log = logger.bind(media_uid=media_uid, filename=filename, size=size)
    log.info("media.processing.started")

    _broadcast(media_uid, status="processing")
    # ... transcode / thumbnail / virus-scan goes here ...
    _broadcast(media_uid, status="done")

    log.info("media.processing.finished")
    return media_uid


def _broadcast(media_uid: str, *, status: str) -> None:
    """Push a status update onto the group for this media item."""
    channel_layer = get_channel_layer()
    if channel_layer is None:  # no CHANNEL_LAYERS configured
        return
    async_to_sync(channel_layer.group_send)(
        f"media.{media_uid}",
        {"type": "media.status", "media_uid": media_uid, "status": status},
    )
