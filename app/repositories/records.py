from typing import Any
from uuid import UUID

from psycopg import Connection, sql

from app.schemas.records import RecordCreate, RecordUpdate

RECORD_COLUMNS = """
    record_id,
    user_id,
    memo,
    emotion,
    satisfaction_score,
    happened_at,
    status,
    created_at,
    updated_at
"""


def create_record(
    connection: Connection[dict[str, Any]],
    user_id: UUID,
    payload: RecordCreate,
) -> dict[str, Any]:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            insert into records (
                user_id,
                memo,
                emotion,
                satisfaction_score,
                happened_at,
                status
            )
            values (%s, %s, %s, %s, %s, 'processing')
            returning {RECORD_COLUMNS}
            """,
            (
                user_id,
                payload.memo,
                payload.emotion,
                payload.satisfaction_score,
                payload.happened_at,
            ),
        )
        row = cursor.fetchone()

    if row is None:
        raise RuntimeError("Failed to create record.")

    return row


def list_records(
    connection: Connection[dict[str, Any]],
    user_id: UUID,
) -> list[dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            select {RECORD_COLUMNS}
            from records
            where user_id = %s
              and deleted_at is null
            order by happened_at desc nulls last, created_at desc
            """,
            (user_id,),
        )
        rows = cursor.fetchall()

    return list(rows)


def get_record(
    connection: Connection[dict[str, Any]],
    user_id: UUID,
    record_id: UUID,
) -> dict[str, Any] | None:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            select {RECORD_COLUMNS}
            from records
            where record_id = %s
              and user_id = %s
              and deleted_at is null
            """,
            (record_id, user_id),
        )
        return cursor.fetchone()


def get_record_by_id(
    connection: Connection[dict[str, Any]],
    record_id: UUID,
) -> dict[str, Any] | None:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            select {RECORD_COLUMNS}
            from records
            where record_id = %s
              and deleted_at is null
            """,
            (record_id,),
        )
        return cursor.fetchone()


def update_record_status(
    connection: Connection[dict[str, Any]],
    record_id: UUID,
    status: str,
) -> dict[str, Any] | None:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            update records
            set status = %s,
                updated_at = now()
            where record_id = %s
              and deleted_at is null
            returning {RECORD_COLUMNS}
            """,
            (status, record_id),
        )
        return cursor.fetchone()


def update_record(
    connection: Connection[dict[str, Any]],
    user_id: UUID,
    record_id: UUID,
    payload: RecordUpdate,
) -> dict[str, Any] | None:
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        return get_record(connection, user_id, record_id)

    assignments = [
        sql.SQL("{} = {}").format(sql.Identifier(column), sql.Placeholder())
        for column in changes
    ]
    assignments.append(sql.SQL("updated_at = now()"))

    query = sql.SQL(
        """
        update records
        set {assignments}
        where record_id = %s
          and user_id = %s
          and deleted_at is null
        returning {columns}
        """
    ).format(
        assignments=sql.SQL(", ").join(assignments),
        columns=sql.SQL(RECORD_COLUMNS),
    )

    with connection.cursor() as cursor:
        cursor.execute(query, [*changes.values(), record_id, user_id])
        return cursor.fetchone()


def delete_record(
    connection: Connection[dict[str, Any]],
    user_id: UUID,
    record_id: UUID,
) -> bool:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            update records
            set status = 'deleted',
                deleted_at = now(),
                updated_at = now()
            where record_id = %s
              and user_id = %s
              and deleted_at is null
            returning record_id
            """,
            (record_id, user_id),
        )
        return cursor.fetchone() is not None
