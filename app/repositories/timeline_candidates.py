from decimal import Decimal
from typing import Any
from uuid import UUID

from psycopg import Connection
from psycopg.types.json import Jsonb

TIMELINE_COLUMNS = """
    timeline_candidate_id,
    user_id,
    record_id,
    timeline_type,
    grouping_key,
    confidence_score,
    reasons,
    created_at
"""


def upsert_timeline_candidate(
    connection: Connection[dict[str, Any]],
    user_id: UUID,
    record_id: UUID,
    timeline_type: str,
    grouping_key: str,
    confidence_score: Decimal | float,
    reasons: dict[str, Any],
) -> dict[str, Any]:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            insert into timeline_candidates (
                user_id,
                record_id,
                timeline_type,
                grouping_key,
                confidence_score,
                reasons
            )
            values (%s, %s, %s, %s, %s, %s)
            on conflict (user_id, record_id, timeline_type, grouping_key)
            do update set
                confidence_score = excluded.confidence_score,
                reasons = excluded.reasons
            returning {TIMELINE_COLUMNS}
            """,
            (
                user_id,
                record_id,
                timeline_type,
                grouping_key,
                confidence_score,
                Jsonb(reasons),
            ),
        )
        row = cursor.fetchone()

    if row is None:
        raise RuntimeError("Failed to upsert timeline candidate.")

    return row


def list_timeline_candidates(
    connection: Connection[dict[str, Any]],
    user_id: UUID,
    record_id: UUID,
) -> list[dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            select {TIMELINE_COLUMNS}
            from timeline_candidates
            where user_id = %s
              and record_id = %s
            order by confidence_score desc nulls last, created_at desc
            """,
            (user_id, record_id),
        )
        rows = cursor.fetchall()

    return list(rows)


def delete_timeline_candidates_for_record(
    connection: Connection[dict[str, Any]],
    record_id: UUID,
) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            delete from timeline_candidates
            where record_id = %s
            """,
            (record_id,),
        )
        return cursor.rowcount
