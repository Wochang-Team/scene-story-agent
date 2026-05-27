from typing import Any
from uuid import UUID

from psycopg import Connection
from psycopg.types.json import Jsonb

EMBEDDING_COLUMNS = """
    embedding_id,
    record_id,
    provider,
    model,
    dimension,
    input_snapshot,
    created_at
"""


def to_vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(str(value) for value in vector) + "]"


def create_embedding(
    connection: Connection[dict[str, Any]],
    record_id: UUID,
    provider: str,
    model: str,
    dimension: int,
    vector: list[float],
    input_snapshot: dict[str, Any],
) -> dict[str, Any]:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            insert into record_embeddings (
                record_id,
                provider,
                model,
                dimension,
                embedding,
                input_snapshot
            )
            values (%s, %s, %s, %s, %s::vector, %s)
            returning {EMBEDDING_COLUMNS}
            """,
            (
                record_id,
                provider,
                model,
                dimension,
                to_vector_literal(vector),
                Jsonb(input_snapshot),
            ),
        )
        row = cursor.fetchone()

    if row is None:
        raise RuntimeError("Failed to create embedding.")

    return row


def get_latest_embedding(
    connection: Connection[dict[str, Any]],
    record_id: UUID,
) -> dict[str, Any] | None:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            select {EMBEDDING_COLUMNS}
            from record_embeddings
            where record_id = %s
              and deleted_at is null
            order by created_at desc
            limit 1
            """,
            (record_id,),
        )
        return cursor.fetchone()


def find_similar_records(
    connection: Connection[dict[str, Any]],
    user_id: UUID,
    source_record_id: UUID,
    vector: list[float],
    dimension: int,
    limit: int,
) -> list[dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            with latest_embeddings as (
                select distinct on (re.record_id)
                    re.record_id,
                    re.embedding,
                    re.dimension,
                    re.created_at
                from record_embeddings re
                join records r on r.record_id = re.record_id
                where r.user_id = %s
                  and r.record_id <> %s
                  and r.deleted_at is null
                  and re.deleted_at is null
                  and re.dimension = %s
                order by re.record_id, re.created_at desc
            )
            select
                le.record_id,
                round((1 - (le.embedding <=> %s::vector))::numeric, 5) as similarity_score
            from latest_embeddings le
            order by le.embedding <=> %s::vector asc
            limit %s
            """,
            (
                user_id,
                source_record_id,
                dimension,
                to_vector_literal(vector),
                to_vector_literal(vector),
                limit,
            ),
        )
        rows = cursor.fetchall()

    return list(rows)


def mark_embeddings_deleted_for_record(
    connection: Connection[dict[str, Any]],
    record_id: UUID,
) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            update record_embeddings
            set deleted_at = now()
            where record_id = %s
              and deleted_at is null
            """,
            (record_id,),
        )
        return cursor.rowcount
