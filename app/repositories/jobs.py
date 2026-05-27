from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from psycopg import Connection

JOB_COLUMNS = """
    job_id,
    record_id,
    job_type,
    status,
    attempt_count,
    last_error_code,
    last_error_message,
    available_at,
    started_at,
    finished_at,
    created_at,
    updated_at
"""

JOB_COLUMNS_WITH_ALIAS = """
    pj.job_id,
    pj.record_id,
    pj.job_type,
    pj.status,
    pj.attempt_count,
    pj.last_error_code,
    pj.last_error_message,
    pj.available_at,
    pj.started_at,
    pj.finished_at,
    pj.created_at,
    pj.updated_at
"""

ACTIVE_STATUSES = ("queued", "running", "retrying")
MAX_ATTEMPTS = 3
BACKOFF_SECONDS = {
    1: 30,
    2: 120,
}


def create_job(
    connection: Connection[dict[str, Any]],
    record_id: UUID,
    job_type: str,
) -> dict[str, Any]:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            insert into processing_jobs (record_id, job_type)
            values (%s, %s)
            returning {JOB_COLUMNS}
            """,
            (record_id, job_type),
        )
        row = cursor.fetchone()

    if row is None:
        raise RuntimeError("Failed to create processing job.")

    return row


def get_active_job_for_record(
    connection: Connection[dict[str, Any]],
    record_id: UUID,
    job_type: str,
) -> dict[str, Any] | None:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            select {JOB_COLUMNS}
            from processing_jobs
            where record_id = %s
              and job_type = %s
              and status = any(%s)
            order by created_at desc
            limit 1
            """,
            (record_id, job_type, list(ACTIVE_STATUSES)),
        )
        return cursor.fetchone()


def get_job(
    connection: Connection[dict[str, Any]],
    job_id: UUID,
) -> dict[str, Any] | None:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            select {JOB_COLUMNS}
            from processing_jobs
            where job_id = %s
            """,
            (job_id,),
        )
        return cursor.fetchone()


def get_job_for_user(
    connection: Connection[dict[str, Any]],
    job_id: UUID,
    user_id: UUID,
) -> dict[str, Any] | None:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            select {JOB_COLUMNS_WITH_ALIAS}
            from processing_jobs pj
            join records r on r.record_id = pj.record_id
            where pj.job_id = %s
              and r.user_id = %s
              and r.deleted_at is null
            """,
            (job_id, user_id),
        )
        return cursor.fetchone()


def list_jobs_for_record(
    connection: Connection[dict[str, Any]],
    record_id: UUID,
) -> list[dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            select {JOB_COLUMNS}
            from processing_jobs
            where record_id = %s
            order by created_at desc
            """,
            (record_id,),
        )
        rows = cursor.fetchall()

    return list(rows)


def list_available_jobs(
    connection: Connection[dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            select {JOB_COLUMNS}
            from processing_jobs
            where status in ('queued', 'retrying')
              and available_at <= now()
            order by available_at asc, created_at asc
            limit %s
            """,
            (limit,),
        )
        rows = cursor.fetchall()

    return list(rows)


def claim_job(
    connection: Connection[dict[str, Any]],
    job_id: UUID,
) -> dict[str, Any] | None:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            update processing_jobs
            set status = 'running',
                started_at = now(),
                finished_at = null,
                updated_at = now()
            where job_id = %s
              and status in ('queued', 'retrying')
              and available_at <= now()
            returning {JOB_COLUMNS}
            """,
            (job_id,),
        )
        return cursor.fetchone()


def mark_succeeded(
    connection: Connection[dict[str, Any]],
    job_id: UUID,
) -> dict[str, Any] | None:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            update processing_jobs
            set status = 'succeeded',
                finished_at = now(),
                updated_at = now()
            where job_id = %s
              and status = 'running'
            returning {JOB_COLUMNS}
            """,
            (job_id,),
        )
        return cursor.fetchone()


def mark_failed(
    connection: Connection[dict[str, Any]],
    job_id: UUID,
    error_code: str,
    error_message: str,
) -> dict[str, Any] | None:
    job = get_job(connection, job_id)
    if job is None or job["status"] != "running":
        return None

    next_attempt_count = job["attempt_count"] + 1
    next_status = "failed" if next_attempt_count >= MAX_ATTEMPTS else "retrying"
    finished_at = datetime.now(timezone.utc) if next_status == "failed" else None
    available_at = datetime.now(timezone.utc) + timedelta(
        seconds=BACKOFF_SECONDS.get(next_attempt_count, BACKOFF_SECONDS[2])
    )

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            update processing_jobs
            set status = %s,
                attempt_count = %s,
                last_error_code = %s,
                last_error_message = %s,
                available_at = %s,
                finished_at = %s,
                updated_at = now()
            where job_id = %s
              and status = 'running'
            returning {JOB_COLUMNS}
            """,
            (
                next_status,
                next_attempt_count,
                error_code,
                error_message,
                available_at,
                finished_at,
                job_id,
            ),
        )
        return cursor.fetchone()


def cancel_job(
    connection: Connection[dict[str, Any]],
    job_id: UUID,
) -> dict[str, Any] | None:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            update processing_jobs
            set status = 'canceled',
                finished_at = now(),
                updated_at = now()
            where job_id = %s
              and status in ('queued', 'running', 'retrying')
            returning {JOB_COLUMNS}
            """,
            (job_id,),
        )
        return cursor.fetchone()


def cancel_active_jobs_for_record(
    connection: Connection[dict[str, Any]],
    record_id: UUID,
) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            update processing_jobs
            set status = 'canceled',
                finished_at = now(),
                updated_at = now()
            where record_id = %s
              and job_type <> 'delete_record_artifacts'
              and status in ('queued', 'running', 'retrying')
            """,
            (record_id,),
        )
        return cursor.rowcount
