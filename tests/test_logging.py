import json
import logging

from app.logging import JsonFormatter, should_log_request


def make_record() -> logging.LogRecord:
    return logging.LogRecord(
        name="scene_story_agent",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request.completed",
        args=(),
        exc_info=None,
    )


def test_json_formatter_uses_single_line_in_production(monkeypatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "production")

    output = JsonFormatter().format(make_record())

    assert "\n" not in output
    payload = json.loads(output)
    assert payload["event"] == "request.completed"
    assert payload["message"] == "request.completed"


def test_json_formatter_keeps_pretty_output_locally(monkeypatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "local")

    output = JsonFormatter().format(make_record())

    assert "\n" in output
    payload = json.loads(output)
    assert payload["event"] == "request.completed"
    assert payload["message"] == "request.completed"


def test_successful_health_check_is_not_logged() -> None:
    assert should_log_request("/health", 200) is False
    assert should_log_request("/health/live", 200) is False
    assert should_log_request("/health/ready", 200) is False


def test_failed_health_check_is_logged() -> None:
    assert should_log_request("/health/live", 500) is True
    assert should_log_request("/health/ready", 503) is True


def test_non_health_request_is_logged() -> None:
    assert should_log_request("/records", 200) is True
