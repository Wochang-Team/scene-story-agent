from decimal import Decimal
from typing import Any
from uuid import UUID

from psycopg import Connection
from psycopg.types.json import Jsonb

RELATION_COLUMNS = """
    relation_id,
    source_record_id,
    target_record_id,
    relation_type,
    similarity_score,
    decision_status,
    reasons,
    created_at,
    updated_at
"""


def upsert_relation(
    connection: Connection[dict[str, Any]],
    source_record_id: UUID,
    target_record_id: UUID,
    relation_type: str,
    similarity_score: Decimal | float,
    reasons: dict[str, Any],
) -> dict[str, Any]:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            insert into record_relations (
                source_record_id,
                target_record_id,
                relation_type,
                similarity_score,
                reasons
            )
            values (%s, %s, %s, %s, %s)
            on conflict (source_record_id, target_record_id, relation_type)
            do update set
                similarity_score = excluded.similarity_score,
                reasons = excluded.reasons,
                updated_at = now()
            returning {RELATION_COLUMNS}
            """,
            (
                source_record_id,
                target_record_id,
                relation_type,
                similarity_score,
                Jsonb(reasons),
            ),
        )
        row = cursor.fetchone()

    if row is None:
        raise RuntimeError("Failed to upsert relation.")

    return row


def list_relations(
    connection: Connection[dict[str, Any]],
    source_record_id: UUID,
) -> list[dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            select {RELATION_COLUMNS}
            from record_relations
            where source_record_id = %s
              and decision_status <> 'hidden'
            order by similarity_score desc nulls last, created_at desc
            """,
            (source_record_id,),
        )
        rows = cursor.fetchall()

    return list(rows)


def hide_relations_for_record(
    connection: Connection[dict[str, Any]],
    record_id: UUID,
) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            update record_relations
            set decision_status = 'hidden',
                updated_at = now()
            where (source_record_id = %s or target_record_id = %s)
              and decision_status <> 'hidden'
            """,
            (record_id, record_id),
        )
        return cursor.rowcount
