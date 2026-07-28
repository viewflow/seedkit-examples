"""Structured logging setup: structlog for app code, ProcessorFormatter so
stdlib records (django, rq, uvicorn) come out through the same renderer.

The ``django_structlog`` middleware binds a per-request ``request_id`` into
structlog's contextvars, so every log line emitted while handling a request
carries it.
"""

from typing import Any

import structlog

_TIMESTAMPER = structlog.processors.TimeStamper(fmt="iso")

_PRE_CHAIN = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    _TIMESTAMPER,
]


def configure_structlog() -> None:
    """Configure structlog to hand events off to stdlib logging."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            _TIMESTAMPER,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def build_logging(log_format: str) -> dict[str, Any]:
    """Return a Django LOGGING dict rendering as ``json`` or ``console``."""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
                "foreign_pre_chain": _PRE_CHAIN,
            },
            "console": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=True),
                "foreign_pre_chain": _PRE_CHAIN,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": log_format,
            },
        },
        "root": {"handlers": ["console"], "level": "INFO"},
        "loggers": {
            "django": {"level": "INFO"},
            "django_structlog": {"level": "INFO"},
            "django.server": {"level": "INFO"},
        },
    }
