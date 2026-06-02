from typing import Any
from uuid import UUID

from psycopg import Connection
from redis import Redis

from app.repositories import jobs as job_repository
from app.services import redis_cache

DEFAULT_JOB_TYPE = "extract_ai_interpretation"
CLAIM_CANDIDATE_LIMIT = 10


def register_record_job(
    connection: Connection[dict[str, Any]],
    redis_client: Redis,
    record_id: UUID,
    job_type: str = DEFAULT_JOB_TYPE,
) -> dict[str, Any]:
    cached_job_id = redis_cache.get_deduped_job_id(redis_client, record_id, job_type)
    if cached_job_id is not None:
        cached_job = job_repository.get_job(connection, cached_job_id)
        if cached_job is not None and cached_job["status"] in job_repository.ACTIVE_STATUSES:
            return cached_job

    active_job = job_repository.get_active_job_for_record(connection, record_id, job_type)
    if active_job is not None:
        redis_cache.set_deduped_job_id(redis_client, record_id, job_type, active_job["job_id"])
        redis_cache.cache_job_state(redis_client, active_job["job_id"], active_job["status"])
        return active_job

    job = job_repository.create_job(connection, record_id, job_type)
    redis_cache.set_deduped_job_id(redis_client, record_id, job_type, job["job_id"])
    redis_cache.cache_job_state(redis_client, job["job_id"], job["status"])
    return job


def claim_next_job(
    connection: Connection[dict[str, Any]],
    redis_client: Redis,
    job_types: list[str] | None = None,
    record_id: UUID | None = None,
) -> tuple[dict[str, Any], str] | None:
    candidates = job_repository.list_available_jobs(
        connection,
        limit=CLAIM_CANDIDATE_LIMIT,
        job_types=job_types,
        record_id=record_id,
    )
    for candidate in candidates:
        lock_token = redis_cache.acquire_job_lock(redis_client, candidate["job_id"])
        if lock_token is None:
            continue

        job = job_repository.claim_job(connection, candidate["job_id"])
        if job is None:
            redis_cache.release_job_lock(redis_client, candidate["job_id"], lock_token)
            continue

        redis_cache.cache_job_state(redis_client, job["job_id"], job["status"])
        return job, lock_token

    return None


def apply_cached_status(redis_client: Redis, job: dict[str, Any]) -> dict[str, Any]:
    cached_status = redis_cache.get_cached_job_state(redis_client, job["job_id"])
    if cached_status is None:
        redis_cache.cache_job_state(redis_client, job["job_id"], job["status"])
        return job

    return {**job, "cached_status": cached_status}
