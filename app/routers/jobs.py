from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import Connection
from redis import Redis

from app.database import get_connection
from app.dependencies import get_current_user_id
from app.redis_client import get_redis
from app.repositories import jobs as job_repository
from app.repositories import records as record_repository
from app.schemas.jobs import JobClaimResponse, JobFailureRequest, JobListResponse, JobLockRequest, JobResponse
from app.services import jobs as job_service
from app.services import redis_cache

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: UUID,
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    redis_client: Annotated[Redis, Depends(get_redis)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> dict[str, Any]:
    job = job_repository.get_job_for_user(connection, job_id, user_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )
    return job_service.apply_cached_status(redis_client, job)


@router.get("/records/{record_id}", response_model=JobListResponse)
def list_record_jobs(
    record_id: UUID,
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    redis_client: Annotated[Redis, Depends(get_redis)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> dict[str, list[dict[str, Any]]]:
    record = record_repository.get_record(connection, user_id, record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found.",
        )

    jobs = [
        job_service.apply_cached_status(redis_client, job)
        for job in job_repository.list_jobs_for_record(connection, record_id)
    ]
    return {"jobs": jobs}


@router.post("/claim", response_model=JobClaimResponse)
def claim_job(
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    redis_client: Annotated[Redis, Depends(get_redis)],
) -> dict[str, Any]:
    claimed = job_service.claim_next_job(connection, redis_client)
    if claimed is None:
        return {"job": None, "lock_token": None}

    job, lock_token = claimed
    connection.commit()
    return {"job": job, "lock_token": lock_token}


@router.post("/{job_id}/succeed", response_model=JobResponse)
def succeed_job(
    job_id: UUID,
    payload: JobLockRequest,
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    redis_client: Annotated[Redis, Depends(get_redis)],
) -> dict[str, Any]:
    job = job_repository.mark_succeeded(connection, job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Running job not found.",
        )

    connection.commit()
    redis_cache.cache_job_state(redis_client, job_id, job["status"])
    redis_cache.release_job_lock(redis_client, job_id, payload.lock_token)
    return job


@router.post("/{job_id}/fail", response_model=JobResponse)
def fail_job(
    job_id: UUID,
    payload: JobFailureRequest,
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    redis_client: Annotated[Redis, Depends(get_redis)],
) -> dict[str, Any]:
    job = job_repository.mark_failed(
        connection=connection,
        job_id=job_id,
        error_code=payload.error_code,
        error_message=payload.error_message,
    )
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Running job not found.",
        )

    connection.commit()
    redis_cache.cache_job_state(redis_client, job_id, job["status"])
    redis_cache.release_job_lock(redis_client, job_id, payload.lock_token)
    return job


@router.post("/{job_id}/cancel", response_model=JobResponse)
def cancel_job(
    job_id: UUID,
    payload: JobLockRequest,
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    redis_client: Annotated[Redis, Depends(get_redis)],
) -> dict[str, Any]:
    job = job_repository.cancel_job(connection, job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active job not found.",
        )

    connection.commit()
    redis_cache.cache_job_state(redis_client, job_id, job["status"])
    redis_cache.release_job_lock(redis_client, job_id, payload.lock_token)
    return job
