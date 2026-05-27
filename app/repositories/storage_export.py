from typing import Any
from uuid import UUID

from psycopg import Connection

from app.schemas.storage import FIELD_CONTRACT


def get_storage_json(
    connection: Connection[dict[str, Any]],
    user_id: UUID,
    record_id: UUID,
) -> dict[str, Any] | None:
    user = fetch_one(
        connection,
        """
        select
            user_id,
            auth_provider,
            auth_subject,
            email,
            display_name,
            created_at,
            updated_at,
            deleted_at
        from app_users
        where user_id = %s
          and deleted_at is null
        """,
        (user_id,),
    )
    record = fetch_one(
        connection,
        """
        select
            record_id,
            user_id,
            memo,
            emotion,
            satisfaction_score,
            happened_at,
            status,
            created_at,
            updated_at,
            deleted_at
        from records
        where record_id = %s
          and user_id = %s
          and deleted_at is null
        """,
        (record_id, user_id),
    )
    if user is None or record is None:
        return None

    return {
        "field_contract": FIELD_CONTRACT,
        "data": {
            "app_users": user,
            "records": record,
            "record_assets": fetch_all(
                connection,
                """
                select
                    asset_id,
                    record_id,
                    asset_type,
                    storage_provider,
                    bucket_name,
                    object_key,
                    content_type,
                    byte_size,
                    width,
                    height,
                    duration_seconds,
                    checksum_sha256,
                    created_at,
                    deleted_at
                from record_assets
                where record_id = %s
                order by created_at asc
                """,
                (record_id,),
            ),
            "record_ai_interpretations": fetch_all(
                connection,
                """
                select
                    interpretation_id,
                    record_id,
                    provider,
                    model,
                    scene_type,
                    summary,
                    ocr_candidates,
                    place_candidates,
                    visit_time_candidates,
                    menu_candidates,
                    activity_candidates,
                    amount_candidates,
                    similar_record_candidates,
                    revisit_candidates,
                    timeline_candidates,
                    tags,
                    user_corrections,
                    raw_response_ref,
                    status,
                    created_at,
                    updated_at,
                    deleted_at
                from record_ai_interpretations
                where record_id = %s
                order by created_at desc
                """,
                (record_id,),
            ),
            "record_embeddings": fetch_all(
                connection,
                """
                select
                    embedding_id,
                    record_id,
                    provider,
                    model,
                    dimension,
                    embedding::text as embedding,
                    input_snapshot,
                    created_at,
                    deleted_at
                from record_embeddings
                where record_id = %s
                order by created_at desc
                """,
                (record_id,),
            ),
            "record_relations": fetch_all(
                connection,
                """
                select
                    relation_id,
                    source_record_id,
                    target_record_id,
                    relation_type,
                    similarity_score,
                    decision_status,
                    reasons,
                    created_at,
                    updated_at
                from record_relations
                where source_record_id = %s
                   or target_record_id = %s
                order by created_at desc
                """,
                (record_id, record_id),
            ),
            "timeline_candidates": fetch_all(
                connection,
                """
                select
                    timeline_candidate_id,
                    user_id,
                    record_id,
                    timeline_type,
                    grouping_key,
                    confidence_score,
                    reasons,
                    created_at
                from timeline_candidates
                where record_id = %s
                order by created_at desc
                """,
                (record_id,),
            ),
            "processing_jobs": fetch_all(
                connection,
                """
                select
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
                from processing_jobs
                where record_id = %s
                order by created_at desc
                """,
                (record_id,),
            ),
        },
    }


def fetch_one(
    connection: Connection[dict[str, Any]],
    query: str,
    params: tuple[Any, ...],
) -> dict[str, Any] | None:
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchone()


def fetch_all(
    connection: Connection[dict[str, Any]],
    query: str,
    params: tuple[Any, ...],
) -> list[dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return list(cursor.fetchall())
