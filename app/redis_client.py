from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from redis import Redis

from app.settings import Settings, get_settings


def get_redis(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Iterator[Redis]:
    client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        socket_connect_timeout=3,
        socket_timeout=3,
        decode_responses=True,
    )
    try:
        yield client
    finally:
        client.close()
