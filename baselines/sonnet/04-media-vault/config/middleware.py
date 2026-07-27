import uuid
from collections.abc import Callable

import structlog
from django.http import HttpRequest, HttpResponse


class RequestIDMiddleware:
    """Binds a per-request `request_id` to structlog's contextvars for the request's lifetime."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = self.get_response(request)
        response["X-Request-ID"] = request_id
        return response
