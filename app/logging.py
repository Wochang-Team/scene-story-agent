from contextvars import ContextVar
from datetime import datetime, timezone
import json
import logging
import sys
from typing import Any
from uuid import uuid4

REQUEST_ID: ContextVar[str | None] = ContextVar("request_id", default=None)
LOGGER_NAME = "scene_story_agent"


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "event": getattr(record, "event", record.getMessage()),
            "request_id": getattr(record, "request_id", None) or REQUEST_ID.get(),
        }
        fields = getattr(record, "fields", None)
        if isinstance(fields, dict):
            payload.update(fields)
        if record.exc_info:
            payload["error_type"] = record.exc_info[0].__name__ if record.exc_info[0] else None
            payload["message"] = str(record.exc_info[1])
        return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


def configure_logging() -> None:
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def set_request_id(request_id: str | None = None) -> str:
    value = request_id or str(uuid4())
    REQUEST_ID.set(value)
    return value


def get_logger() -> logging.Logger:
    configure_logging()
    return logging.getLogger(LOGGER_NAME)


def log_event(
    event: str,
    level: int = logging.INFO,
    **fields: Any,
) -> None:
    get_logger().log(
        level,
        event,
        extra={
            "event": event,
            "request_id": REQUEST_ID.get(),
            "fields": sanitize_fields(fields),
        },
    )


def sanitize_fields(fields: dict[str, Any]) -> dict[str, Any]:
    redacted_keys = {"api_key", "authorization", "data_base64", "image_base64"}
    sanitized = {}
    for key, value in fields.items():
        if key.lower() in redacted_keys:
            sanitized[key] = "[redacted]"
        else:
            sanitized[key] = value
    return sanitized
