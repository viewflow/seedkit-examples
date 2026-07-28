"""structlog wiring: JSON in production, human-readable console in dev.

Everything (Django's own loggers included) is routed through structlog's
``ProcessorFormatter`` so third-party log records get the same shape and the
same request-scoped context as our own ``structlog.get_logger()`` calls.
"""

import uuid
from collections.abc import Awaitable, Callable
from typing import Any

import structlog
from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.http import HttpRequest, HttpResponse

REQUEST_ID_HEADER = "X-Request-ID"

#: Processors applied to records that did *not* originate from structlog
#: (Django, uvicorn, boto3, ...) before they reach the formatter.
_FOREIGN_PRE_CHAIN: list[Any] = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
    structlog.dev.set_exc_info,
]


def configure_structlog(*, json_logs: bool) -> None:
    """Configure the structlog side of the pipeline. Safe to call repeatedly."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=not json_logs,
    )


def build_logging_config(*, json_logs: bool, level: str) -> dict[str, Any]:
    """Return a ``LOGGING`` dict wiring stdlib logging into structlog."""
    formatter = "json" if json_logs else "console"
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processors": [
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.processors.dict_tracebacks,
                    structlog.processors.JSONRenderer(),
                ],
                "foreign_pre_chain": _FOREIGN_PRE_CHAIN,
            },
            "console": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processors": [
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.dev.ConsoleRenderer(colors=True),
                ],
                "foreign_pre_chain": _FOREIGN_PRE_CHAIN,
            },
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": formatter,
            },
        },
        "root": {"handlers": ["default"], "level": level},
        "loggers": {
            # The access log is uvicorn's job; Django's duplicate is noise.
            "django.server": {"propagate": True, "level": "WARNING"},
            "django.db.backends": {"propagate": True, "level": "WARNING"},
            "django.utils.autoreload": {"propagate": True, "level": "WARNING"},
        },
    }


class RequestIDMiddleware:
    """Bind a ``request_id`` (plus method/path) into the structlog context.

    Honours an inbound ``X-Request-ID`` so a request can be traced across
    services, and echoes it back on the response.
    """

    sync_capable = True
    async_capable = True

    def __init__(
        self,
        get_response: Callable[[HttpRequest], HttpResponse]
        | Callable[[HttpRequest], Awaitable[HttpResponse]],
    ) -> None:
        self.get_response = get_response
        self._is_async = iscoroutinefunction(get_response)
        if self._is_async:
            markcoroutinefunction(self)

    def __call__(self, request: HttpRequest) -> Any:
        if self._is_async:
            return self._acall(request)
        request_id = self._bind(request)
        response = self.get_response(request)  # type: ignore[return-value]
        return self._unbind(response, request_id)  # type: ignore[arg-type]

    async def _acall(self, request: HttpRequest) -> HttpResponse:
        request_id = self._bind(request)
        response = await self.get_response(request)  # type: ignore[misc]
        return self._unbind(response, request_id)

    def _bind(self, request: HttpRequest) -> str:
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.path,
        )
        return request_id

    def _unbind(self, response: HttpResponse, request_id: str) -> HttpResponse:
        response[REQUEST_ID_HEADER] = request_id
        structlog.contextvars.clear_contextvars()
        return response
