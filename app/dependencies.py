from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from psycopg import Connection
from redis import Redis

from app.database import get_connection
from app.redis_client import get_redis
from app.repositories.users import LOCAL_AUTH_PROVIDER, ensure_local_user
from app.services.redis_cache import cache_user_id, get_cached_user_id


def get_local_auth_subject(
    x_local_user: Annotated[str | None, Header(alias="X-Local-User")] = None,
) -> str:
    auth_subject = (x_local_user or "local-user").strip()
    if not auth_subject:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Local-User header must not be empty.",
        )
    return auth_subject


def get_current_user_id(
    connection: Annotated[Connection[dict], Depends(get_connection)],
    redis_client: Annotated[Redis, Depends(get_redis)],
    auth_subject: Annotated[str, Depends(get_local_auth_subject)],
) -> UUID:
    cached_user_id = get_cached_user_id(redis_client, LOCAL_AUTH_PROVIDER, auth_subject)
    if cached_user_id is not None:
        return cached_user_id

    user_id = ensure_local_user(connection, auth_subject)
    cache_user_id(redis_client, LOCAL_AUTH_PROVIDER, auth_subject, user_id)
    return user_id
