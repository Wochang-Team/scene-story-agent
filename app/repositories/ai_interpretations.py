from typing import Any
from uuid import UUID

from psycopg import Connection
from psycopg.types.json import Jsonb

from app.schemas.ai import SceneAnalysisResult

INTERPRETATION_COLUMNS = """
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
    updated_at
"""


def create_interpretation(
    connection: Connection[dict[str, Any]],
    record_id: UUID,
    result: SceneAnalysisResult,
) -> dict[str, Any]:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            insert into record_ai_interpretations (
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
                raw_response_ref,
                status
            )
            values (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s,
                'completed'
            )
            returning {INTERPRETATION_COLUMNS}
            """,
            (
                record_id,
                result.provider,
                result.model,
                result.scene_type,
                result.summary,
                Jsonb(result.ocr_candidates),
                Jsonb(result.place_candidates),
                Jsonb(result.visit_time_candidates),
                Jsonb(result.menu_candidates),
                Jsonb(result.activity_candidates),
                Jsonb(result.amount_candidates),
                Jsonb(result.similar_record_candidates),
                Jsonb(result.revisit_candidates),
                Jsonb(result.timeline_candidates),
                Jsonb(result.tags),
                Jsonb(result.raw_response_ref),
            ),
        )
        row = cursor.fetchone()

    if row is None:
        raise RuntimeError("Failed to create AI interpretation.")

    return row


def get_latest_interpretation(
    connection: Connection[dict[str, Any]],
    record_id: UUID,
) -> dict[str, Any] | None:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            select {INTERPRETATION_COLUMNS}
            from record_ai_interpretations
            where record_id = %s
              and deleted_at is null
            order by created_at desc
            limit 1
            """,
            (record_id,),
        )
        return cursor.fetchone()


def mark_interpretations_deleted_for_record(
    connection: Connection[dict[str, Any]],
    record_id: UUID,
) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            update record_ai_interpretations
            set deleted_at = now(),
                updated_at = now()
            where record_id = %s
              and deleted_at is null
            """,
            (record_id,),
        )
        return cursor.rowcount
