import json
from secrets import token_urlsafe
from uuid import UUID

from redis import Redis

JOB_LOCK_TTL_SECONDS = 300
JOB_STATE_TTL_SECONDS = 60
JOB_DEDUPE_TTL_SECONDS = 300
AUTH_USER_TTL_SECONDS = 3600
PROFILE_TTL_SECONDS = 600
SESSION_TTL_SECONDS = 7 * 24 * 60 * 60
AUTH_RATE_TTL_SECONDS = 60


def job_lock_key(job_id: UUID) -> str:
    return f"job:lock:{job_id}"


def job_state_key(job_id: UUID) -> str:
    return f"job:state:{job_id}"


def job_dedupe_key(record_id: UUID, job_type: str) -> str:
    return f"record:job:dedupe:{record_id}:{job_type}"


def auth_user_key(auth_provider: str, auth_subject: str) -> str:
    return f"user:auth:{auth_provider}:{auth_subject}"


def user_profile_key(user_id: UUID) -> str:
    return f"user:profile:{user_id}"


def session_key(session_id: str) -> str:
    return f"session:{session_id}"


def auth_rate_key(key: str) -> str:
    return f"auth:rate:{key}"


def acquire_job_lock(redis_client: Redis, job_id: UUID) -> str | None:
    lock_token = token_urlsafe(24)
    acquired = redis_client.set(
        job_lock_key(job_id),
        lock_token,
        nx=True,
        ex=JOB_LOCK_TTL_SECONDS,
    )
    if not acquired:
        return None
    return lock_token


def release_job_lock(redis_client: Redis, job_id: UUID, lock_token: str | None) -> bool:
    if not lock_token:
        return False

    script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    end
    return 0
    """
    result = redis_client.eval(script, 1, job_lock_key(job_id), lock_token)
    return result == 1


def cache_job_state(redis_client: Redis, job_id: UUID, status: str) -> None:
    redis_client.set(job_state_key(job_id), status, ex=JOB_STATE_TTL_SECONDS)


def get_cached_job_state(redis_client: Redis, job_id: UUID) -> str | None:
    return redis_client.get(job_state_key(job_id))


def set_deduped_job_id(redis_client: Redis, record_id: UUID, job_type: str, job_id: UUID) -> None:
    redis_client.set(
        job_dedupe_key(record_id, job_type),
        str(job_id),
        ex=JOB_DEDUPE_TTL_SECONDS,
    )


def get_deduped_job_id(redis_client: Redis, record_id: UUID, job_type: str) -> UUID | None:
    value = redis_client.get(job_dedupe_key(record_id, job_type))
    if value is None:
        return None
    return UUID(value)


def cache_user_id(
    redis_client: Redis,
    auth_provider: str,
    auth_subject: str,
    user_id: UUID,
) -> None:
    redis_client.set(
        auth_user_key(auth_provider, auth_subject),
        str(user_id),
        ex=AUTH_USER_TTL_SECONDS,
    )


def get_cached_user_id(
    redis_client: Redis,
    auth_provider: str,
    auth_subject: str,
) -> UUID | None:
    value = redis_client.get(auth_user_key(auth_provider, auth_subject))
    if value is None:
        return None
    return UUID(value)


def cache_user_profile(redis_client: Redis, user_id: UUID, profile: dict[str, str | None]) -> None:
    redis_client.set(user_profile_key(user_id), json.dumps(profile), ex=PROFILE_TTL_SECONDS)


def get_cached_user_profile(redis_client: Redis, user_id: UUID) -> dict[str, str | None] | None:
    value = redis_client.get(user_profile_key(user_id))
    if value is None:
        return None
    return json.loads(value)


def set_session(redis_client: Redis, session_id: str, session_data: dict[str, str]) -> None:
    redis_client.set(session_key(session_id), json.dumps(session_data), ex=SESSION_TTL_SECONDS)


def get_session(redis_client: Redis, session_id: str) -> dict[str, str] | None:
    value = redis_client.get(session_key(session_id))
    if value is None:
        return None
    return json.loads(value)


def delete_session(redis_client: Redis, session_id: str) -> None:
    redis_client.delete(session_key(session_id))


def hit_auth_rate_limit(redis_client: Redis, key: str, limit: int) -> bool:
    redis_key = auth_rate_key(key)
    count = redis_client.incr(redis_key)
    if count == 1:
        redis_client.expire(redis_key, AUTH_RATE_TTL_SECONDS)
    return count > limit
