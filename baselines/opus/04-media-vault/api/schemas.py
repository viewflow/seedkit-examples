"""Request/response schemas for the public API."""

import uuid

import msgspec


class MediaCreateRequest(msgspec.Struct, frozen=True):
    """Client-declared metadata for an upload that is about to happen."""

    filename: str
    size: int


class MediaCreateResponse(msgspec.Struct, frozen=True):
    """Handle the client uses to follow the upload over ``/ws/echo/``."""

    uid: uuid.UUID
    filename: str
