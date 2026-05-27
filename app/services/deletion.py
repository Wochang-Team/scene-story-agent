from dataclasses import dataclass
from typing import Any
from uuid import UUID

from psycopg import Connection

from app.repositories import ai_interpretations as interpretation_repository
from app.repositories import assets as asset_repository
from app.repositories import embeddings as embedding_repository
from app.repositories import jobs as job_repository
from app.repositories import records as record_repository
from app.repositories import relations as relation_repository
from app.repositories import timeline_candidates as timeline_repository
from app.services.storage import LocalStorage
from app.settings import Settings


@dataclass(frozen=True)
class DeleteRecordResult:
    deleted: bool
    file_error_count: int
    compensation_job_id: UUID | None


def delete_record_graph(
    connection: Connection[dict[str, Any]],
    settings: Settings,
    user_id: UUID,
    record_id: UUID,
) -> DeleteRecordResult:
    record = record_repository.get_record(connection, user_id, record_id)
    if record is None:
        return DeleteRecordResult(
            deleted=False,
            file_error_count=0,
            compensation_job_id=None,
        )

    storage = LocalStorage(settings)
    assets = asset_repository.list_assets(connection, record_id)
    file_errors = []
    for asset in assets:
        try:
            storage.delete(asset["object_key"])
        except OSError as exc:
            file_errors.append({"object_key": asset["object_key"], "error": str(exc)})

    deleted = record_repository.delete_record(connection, user_id, record_id)
    asset_repository.mark_assets_deleted_for_record(connection, record_id)
    interpretation_repository.mark_interpretations_deleted_for_record(connection, record_id)
    embedding_repository.mark_embeddings_deleted_for_record(connection, record_id)
    relation_repository.hide_relations_for_record(connection, record_id)
    timeline_repository.delete_timeline_candidates_for_record(connection, record_id)
    job_repository.cancel_active_jobs_for_record(connection, record_id)

    compensation_job_id = None
    if file_errors:
        compensation_job = job_repository.create_job(
            connection=connection,
            record_id=record_id,
            job_type="delete_record_artifacts",
        )
        compensation_job_id = compensation_job["job_id"]

    return DeleteRecordResult(
        deleted=deleted,
        file_error_count=len(file_errors),
        compensation_job_id=compensation_job_id,
    )
