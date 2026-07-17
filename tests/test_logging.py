import json
import logging

from app.logging import JsonFormatter


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
    assert json.loads(output)["event"] == "request.completed"


def test_json_formatter_keeps_pretty_output_locally(monkeypatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "local")

    output = JsonFormatter().format(make_record())

    assert "\n" in output
    assert json.loads(output)["event"] == "request.completed"
