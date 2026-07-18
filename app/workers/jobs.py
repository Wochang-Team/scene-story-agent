from time import sleep
from typing import Any

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row
from redis import Redis

from app.logging import log_event
from app.providers.http import ProviderHttpError
from app.repositories import jobs as job_repository
from app.repositories import records as record_repository
from app.services import ai_pipeline
from app.services import embedding_pipeline
from app.services import jobs as job_service
from app.services import redis_cache
from app.settings import Settings, get_settings

POLL_INTERVAL_SECONDS = 1
WORKER_JOB_TYPES = [job_service.DEFAULT_JOB_TYPE]


def process_next_job(
    connection: Connection[dict[str, Any]],
    redis_client: Redis,
    settings: Settings,
    record_id: Any | None = None,
) -> bool:
    claimed = job_service.claim_next_job(
        connection,
        redis_client,
        job_types=WORKER_JOB_TYPES,
        record_id=record_id,
    )
    if claimed is None:
        connection.rollback()
        return False

    job, lock_token = claimed
    connection.commit()

    try:
        process_job(connection, settings, job)
        succeeded_job = job_repository.mark_succeeded(connection, job["job_id"])
        if succeeded_job is None:
            raise RuntimeError("Running job not found during success update.")
        record_repository.update_record_status(connection, job["record_id"], "ready")
        connection.commit()
        redis_cache.cache_job_state(redis_client, job["job_id"], succeeded_job["status"])
        log_event(
            "worker.job_succeeded",
            job_id=str(job["job_id"]),
            record_id=str(job["record_id"]),
            job_type=job["job_type"],
            status=succeeded_job["status"],
        )
    except Exception as exc:
        connection.rollback()
        failed_job = job_repository.mark_failed(
            connection=connection,
            job_id=job["job_id"],
            error_code=job_error_code(exc),
            error_message=str(exc)[:500],
        )
        if failed_job is None:
            connection.rollback()
            log_event(
                "worker.job_fail_update_failed",
                job_id=str(job["job_id"]),
                record_id=str(job["record_id"]),
                job_type=job["job_type"],
                error_type=type(exc).__name__,
                message=str(exc),
            )
        else:
            if failed_job["status"] == "failed":
                record_repository.update_record_status(connection, job["record_id"], "failed")
            connection.commit()
            redis_cache.cache_job_state(redis_client, job["job_id"], failed_job["status"])
            log_event(
                "worker.job_failed",
                job_id=str(job["job_id"]),
                record_id=str(job["record_id"]),
                job_type=job["job_type"],
                status=failed_job["status"],
                attempt_count=failed_job["attempt_count"],
                last_error_code=failed_job["last_error_code"],
            )
    finally:
        redis_cache.release_job_lock(redis_client, job["job_id"], lock_token)

    return True


def process_job(
    connection: Connection[dict[str, Any]],
    settings: Settings,
    job: dict[str, Any],
) -> None:
    if job["job_type"] != job_service.DEFAULT_JOB_TYPE:
        raise RuntimeError(f"Unsupported worker job type: {job['job_type']}")

    record = record_repository.get_record_by_id(connection, job["record_id"])
    if record is None:
        raise RuntimeError("Record not found for AI interpretation job.")

    ai_pipeline.analyze_record(
        connection=connection,
        settings=settings,
        record=record,
    )
    embedding_pipeline.build_embedding_and_candidates(
        connection=connection,
        settings=settings,
        user_id=record["user_id"],
        record=record,
    )


def job_error_code(exc: Exception) -> str:
    if isinstance(exc, ProviderHttpError):
        message = str(exc)
        if "Lightning dunning decision" in message:
            return "provider_dunning_denied"
        if "HTTP 403" in message:
            return "provider_http_403"
        if "HTTP 429" in message:
            return "provider_http_429"
        return "provider_http_error"
    if isinstance(exc, ValueError):
        return "invalid_ai_input"
    return type(exc).__name__


def run_forever(
    settings: Settings | None = None,
    poll_interval_seconds: int = POLL_INTERVAL_SECONDS,
) -> None:
    resolved_settings = settings or get_settings()
    redis_client = Redis(
        host=resolved_settings.redis_host,
        port=resolved_settings.redis_port,
        socket_connect_timeout=3,
        socket_timeout=3,
        decode_responses=True,
    )
    try:
        with psycopg.connect(
            **resolved_settings.postgres_connection_kwargs,
            row_factory=dict_row,
        ) as connection:
            log_event(
                "worker.started",
                job_types=WORKER_JOB_TYPES,
                poll_interval_seconds=poll_interval_seconds,
            )
            while True:
                processed = process_next_job(connection, redis_client, resolved_settings)
                if not processed:
                    sleep(poll_interval_seconds)
    finally:
        redis_client.close()


def main() -> None:
    run_forever()


if __name__ == "__main__":
    main()
