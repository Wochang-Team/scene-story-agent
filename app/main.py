from time import monotonic
from typing import Any

from fastapi import FastAPI
from fastapi import Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
import psycopg
from redis import Redis

from app.logging import configure_logging, log_event, set_request_id
from app.routers.jobs import router as jobs_router
from app.routers.records import router as records_router
from app.routers.ui import router as ui_router
from app.settings import get_settings

configure_logging()

app = FastAPI(title="scene-story-agent")
app.include_router(jobs_router)
app.include_router(records_router)
app.include_router(ui_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    log_event(
        "request.validation_failed",
        message=f"{request.method} {request.url.path} -> 422 (validation failed)",
        method=request.method,
        path=request.url.path,
        status_code=422,
        errors=format_validation_errors(exc.errors()),
    )
    return await request_validation_exception_handler(request, exc)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = set_request_id(request.headers.get("X-Request-ID"))
    started_at = monotonic()
    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = round((monotonic() - started_at) * 1000, 2)
        log_event(
            "request.failed",
            method=request.method,
            path=request.url.path,
            status_code=500,
            duration_ms=duration_ms,
            error_type=type(exc).__name__,
            message=(
                f"{request.method} {request.url.path} -> 500 "
                f"({duration_ms:.2f} ms): {type(exc).__name__}: {exc}"
            ),
        )
        raise

    duration_ms = round((monotonic() - started_at) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    if response.status_code >= 500:
        event = "request.failed"
    elif response.status_code >= 400:
        event = "request.client_error"
    else:
        event = "request.completed"
    log_event(
        event,
        message=(
            f"{request.method} {request.url.path} -> {response.status_code} "
            f"({duration_ms:.2f} ms)"
        ),
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
    )
    return response


def format_validation_errors(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    formatted = []
    for error in errors:
        loc = list(error.get("loc", []))
        item = {
            "type": error.get("type"),
            "loc": loc,
            "msg": error.get("msg"),
        }
        if loc and loc[0] in {"path", "query", "header"}:
            item["input"] = error.get("input")
        ctx = error.get("ctx")
        if ctx:
            item["ctx"] = ctx
        formatted.append(item)
    return formatted


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "scene-story-agent API"}


@app.get("/health")
@app.get("/health/live")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready")
async def readiness() -> dict[str, str | dict[str, str]]:
    settings = get_settings()

    log_event(
        "database.connection_attempt",
        environment=settings.postgres_log_environment,
    )
    with psycopg.connect(
        **settings.postgres_connection_kwargs,
        connect_timeout=3,
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("select 1")
            cursor.fetchone()

    # redis_client = Redis(
    #     host=settings.redis_host,
    #     port=settings.redis_port,
    #     socket_connect_timeout=3,
    #     socket_timeout=3,
    #     decode_responses=True,
    # )
    # redis_client.ping()

    return {
        "status": "ok",
        "dependencies": {
            "postgres": "ok",
            "redis": "ok",
        },
    }
