from fastapi import FastAPI
import psycopg
from redis import Redis

from app.settings import get_settings

app = FastAPI(title="scene-story-agent")


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "scene-story-agent API"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready")
async def readiness() -> dict[str, str | dict[str, str]]:
    settings = get_settings()

    with psycopg.connect(settings.postgres_dsn, connect_timeout=3) as conn:
        with conn.cursor() as cursor:
            cursor.execute("select 1")
            cursor.fetchone()

    redis_client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        socket_connect_timeout=3,
        socket_timeout=3,
        decode_responses=True,
    )
    redis_client.ping()

    return {
        "status": "ok",
        "dependencies": {
            "postgres": "ok",
            "redis": "ok",
        },
    }
