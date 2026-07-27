import uuid

import structlog

logger = structlog.get_logger(__name__)


class RequestIDMiddleware:
    """Binds a request-scoped `request_id` to every structlog log line."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        structlog.contextvars.clear_contextvars()
        request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = self.get_response(request)

        response["X-Request-Id"] = request_id
        return response
