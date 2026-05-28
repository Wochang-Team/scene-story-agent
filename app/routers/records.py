from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse
from psycopg import Connection
from redis import Redis

from app.database import get_connection
from app.dependencies import get_current_user_id
from app.logging import log_event
from app.redis_client import get_redis
from app.repositories import assets as asset_repository
from app.repositories import ai_interpretations as interpretation_repository
from app.repositories import records as record_repository
from app.repositories import relations as relation_repository
from app.repositories import storage_export as storage_export_repository
from app.repositories import timeline_candidates as timeline_repository
from app.schemas.assets import AssetListResponse, AssetResponse
from app.schemas.ai import SceneAnalysisResponse
from app.schemas.embeddings import EmbeddingBuildResponse, RelationListResponse, TimelineCandidateListResponse
from app.schemas.records import RecordCreate, RecordListResponse, RecordResponse, RecordUpdate
from app.schemas.storage import StorageExportResponse
from app.services import ai_pipeline
from app.services import deletion as deletion_service
from app.services import embedding_pipeline
from app.services import jobs as job_service
from app.services.storage import LocalStorage
from app.settings import Settings, get_settings
from app.providers.http import ProviderHttpError

router = APIRouter(prefix="/records", tags=["records"])


@router.post("", response_model=RecordResponse, status_code=status.HTTP_201_CREATED)
def create_record(
    payload: RecordCreate,
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    redis_client: Annotated[Redis, Depends(get_redis)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> dict[str, Any]:
    record = record_repository.create_record(connection, user_id, payload)
    job = job_service.register_record_job(connection, redis_client, record["record_id"])
    connection.commit()
    log_event(
        "record.created",
        user_id=str(user_id),
        record_id=str(record["record_id"]),
        status=record["status"],
    )
    log_event(
        "job.created",
        record_id=str(record["record_id"]),
        job_id=str(job["job_id"]),
        job_type=job["job_type"],
        status=job["status"],
    )
    return record


@router.get("", response_model=RecordListResponse)
def list_records(
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> dict[str, list[dict[str, Any]]]:
    records = record_repository.list_records(connection, user_id)
    return {"records": records}


@router.get("/{record_id}", response_model=RecordResponse)
def get_record(
    record_id: UUID,
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> dict[str, Any]:
    record = record_repository.get_record(connection, user_id, record_id)
    if record is None:
        log_event("record.not_found", user_id=str(user_id), record_id=str(record_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found.",
        )
    return record


@router.get("/{record_id}/storage-json", response_model=StorageExportResponse)
def get_record_storage_json(
    record_id: UUID,
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> dict[str, Any]:
    storage_json = storage_export_repository.get_storage_json(
        connection=connection,
        user_id=user_id,
        record_id=record_id,
    )
    if storage_json is None:
        log_event("record.not_found", user_id=str(user_id), record_id=str(record_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found.",
        )

    data = storage_json["data"]
    log_event(
        "storage_json.read",
        user_id=str(user_id),
        record_id=str(record_id),
        asset_count=len(data["record_assets"]),
        ai_interpretation_count=len(data["record_ai_interpretations"]),
        embedding_count=len(data["record_embeddings"]),
        relation_count=len(data["record_relations"]),
        timeline_candidate_count=len(data["timeline_candidates"]),
        job_count=len(data["processing_jobs"]),
    )
    return storage_json


@router.patch("/{record_id}", response_model=RecordResponse)
def update_record(
    record_id: UUID,
    payload: RecordUpdate,
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> dict[str, Any]:
    record = record_repository.update_record(connection, user_id, record_id, payload)
    if record is None:
        log_event("record.not_found", user_id=str(user_id), record_id=str(record_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found.",
        )

    connection.commit()
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: UUID,
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    result = deletion_service.delete_record_graph(
        connection=connection,
        settings=settings,
        user_id=user_id,
        record_id=record_id,
    )
    if not result.deleted:
        log_event("record.not_found", user_id=str(user_id), record_id=str(record_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found.",
        )

    connection.commit()
    log_event(
        "record.deleted",
        user_id=str(user_id),
        record_id=str(record_id),
        file_error_count=result.file_error_count,
        compensation_job_id=str(result.compensation_job_id) if result.compensation_job_id else None,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{record_id}/ai-analysis", response_model=SceneAnalysisResponse)
def analyze_record_scene(
    record_id: UUID,
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any]:
    record = record_repository.get_record(connection, user_id, record_id)
    if record is None:
        log_event("record.not_found", user_id=str(user_id), record_id=str(record_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found.",
        )

    try:
        interpretation = ai_pipeline.analyze_record(
            connection=connection,
            settings=settings,
            record=record,
        )
    except NotImplementedError as exc:
        log_event("ai.analysis_failed", user_id=str(user_id), record_id=str(record_id), error_type=type(exc).__name__, message=str(exc))
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        log_event("ai.analysis_failed", user_id=str(user_id), record_id=str(record_id), error_type=type(exc).__name__, message=str(exc))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ProviderHttpError as exc:
        log_event("ai.provider_failed", user_id=str(user_id), record_id=str(record_id), error_type=type(exc).__name__, message=str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    connection.commit()
    log_event(
        "ai.analysis.completed",
        user_id=str(user_id),
        record_id=str(record_id),
        interpretation_id=str(interpretation["interpretation_id"]),
        provider=interpretation["provider"],
        model=interpretation["model"],
        ocr_candidate_count=len(interpretation["ocr_candidates"] or []),
        place_candidate_count=len(interpretation["place_candidates"] or []),
        menu_candidate_count=len(interpretation["menu_candidates"] or []),
        activity_candidate_count=len(interpretation["activity_candidates"] or []),
        amount_candidate_count=len(interpretation["amount_candidates"] or []),
        tag_count=len(interpretation["tags"] or []),
    )
    return interpretation


@router.get("/{record_id}/ai-analysis", response_model=SceneAnalysisResponse)
def get_latest_record_scene_analysis(
    record_id: UUID,
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> dict[str, Any]:
    record = record_repository.get_record(connection, user_id, record_id)
    if record is None:
        log_event("record.not_found", user_id=str(user_id), record_id=str(record_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found.",
        )

    interpretation = interpretation_repository.get_latest_interpretation(
        connection=connection,
        record_id=record_id,
    )
    if interpretation is None:
        log_event("ai.analysis_not_found", user_id=str(user_id), record_id=str(record_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI analysis not found.",
        )

    return interpretation


@router.post(
    "/{record_id}/assets",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_asset(
    record_id: UUID,
    file: Annotated[UploadFile, File()],
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any]:
    record = record_repository.get_record(connection, user_id, record_id)
    if record is None:
        log_event("record.not_found", user_id=str(user_id), record_id=str(record_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found.",
        )

    storage = LocalStorage(settings)
    try:
        stored_file = await storage.save_upload(user_id, record_id, file)
    except HTTPException as exc:
        log_event(
            "asset.store_failed",
            user_id=str(user_id),
            record_id=str(record_id),
            content_type=file.content_type,
            status_code=exc.status_code,
            message=str(exc.detail),
        )
        raise

    try:
        asset = asset_repository.create_asset(
            connection=connection,
            record_id=record_id,
            asset_type=stored_file.asset_type,
            bucket_name=stored_file.bucket_name,
            object_key=stored_file.object_key,
            content_type=stored_file.content_type,
            byte_size=stored_file.byte_size,
            checksum_sha256=stored_file.checksum_sha256,
        )
        connection.commit()
    except Exception:
        storage.delete(stored_file.object_key)
        log_event(
            "asset.store_failed",
            user_id=str(user_id),
            record_id=str(record_id),
            content_type=stored_file.content_type,
            byte_size=stored_file.byte_size,
        )
        raise

    log_event(
        "asset.stored",
        user_id=str(user_id),
        record_id=str(record_id),
        asset_id=str(asset["asset_id"]),
        asset_type=asset["asset_type"],
        content_type=asset["content_type"],
        byte_size=asset["byte_size"],
        checksum_sha256=asset["checksum_sha256"],
    )
    return asset


@router.get("/{record_id}/assets", response_model=AssetListResponse)
def list_assets(
    record_id: UUID,
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> dict[str, list[dict[str, Any]]]:
    record = record_repository.get_record(connection, user_id, record_id)
    if record is None:
        log_event("record.not_found", user_id=str(user_id), record_id=str(record_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found.",
        )

    assets = asset_repository.list_assets(connection, record_id)
    return {"assets": assets}


@router.get("/{record_id}/assets/{asset_id}/file")
def download_asset(
    record_id: UUID,
    asset_id: UUID,
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> FileResponse:
    record = record_repository.get_record(connection, user_id, record_id)
    if record is None:
        log_event("record.not_found", user_id=str(user_id), record_id=str(record_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found.",
        )

    asset = asset_repository.get_asset(connection, record_id, asset_id)
    if asset is None:
        log_event("asset.not_found", user_id=str(user_id), record_id=str(record_id), asset_id=str(asset_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    path = LocalStorage(settings).resolve_path(asset["object_key"])
    if not path.exists():
        log_event("asset.file_not_found", user_id=str(user_id), record_id=str(record_id), asset_id=str(asset_id), object_key=asset["object_key"])
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset file not found.",
        )

    return FileResponse(path=path, media_type=asset["content_type"])


@router.delete("/{record_id}/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    record_id: UUID,
    asset_id: UUID,
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    record = record_repository.get_record(connection, user_id, record_id)
    if record is None:
        log_event("record.not_found", user_id=str(user_id), record_id=str(record_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found.",
        )

    asset = asset_repository.get_asset(connection, record_id, asset_id)
    if asset is None:
        log_event("asset.not_found", user_id=str(user_id), record_id=str(record_id), asset_id=str(asset_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    LocalStorage(settings).delete(asset["object_key"])
    deleted = asset_repository.mark_asset_deleted(connection, record_id, asset_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    connection.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{record_id}/embedding", response_model=EmbeddingBuildResponse)
def build_record_embedding(
    record_id: UUID,
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any]:
    record = record_repository.get_record(connection, user_id, record_id)
    if record is None:
        log_event("record.not_found", user_id=str(user_id), record_id=str(record_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found.",
        )

    try:
        result = embedding_pipeline.build_embedding_and_candidates(
            connection=connection,
            settings=settings,
            user_id=user_id,
            record=record,
        )
    except NotImplementedError as exc:
        log_event("embedding.failed", user_id=str(user_id), record_id=str(record_id), error_type=type(exc).__name__, message=str(exc))
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(exc),
        ) from exc

    connection.commit()
    log_event(
        "embedding.created",
        user_id=str(user_id),
        record_id=str(record_id),
        embedding_id=str(result["embedding"]["embedding_id"]),
        provider=result["embedding"]["provider"],
        model=result["embedding"]["model"],
        dimension=result["embedding"]["dimension"],
    )
    log_event(
        "relations.created",
        user_id=str(user_id),
        record_id=str(record_id),
        relation_count=len(result["relations"]),
    )
    log_event(
        "timeline.created",
        user_id=str(user_id),
        record_id=str(record_id),
        timeline_candidate_count=len(result["timeline_candidates"]),
    )
    return result


@router.get("/{record_id}/relations", response_model=RelationListResponse)
def list_record_relations(
    record_id: UUID,
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> dict[str, list[dict[str, Any]]]:
    record = record_repository.get_record(connection, user_id, record_id)
    if record is None:
        log_event("record.not_found", user_id=str(user_id), record_id=str(record_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found.",
        )

    relations = relation_repository.list_relations(connection, record_id)
    return {"relations": relations}


@router.get("/{record_id}/timeline-candidates", response_model=TimelineCandidateListResponse)
def list_record_timeline_candidates(
    record_id: UUID,
    connection: Annotated[Connection[dict[str, Any]], Depends(get_connection)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> dict[str, list[dict[str, Any]]]:
    record = record_repository.get_record(connection, user_id, record_id)
    if record is None:
        log_event("record.not_found", user_id=str(user_id), record_id=str(record_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found.",
        )

    timeline_candidates = timeline_repository.list_timeline_candidates(
        connection=connection,
        user_id=user_id,
        record_id=record_id,
    )
    return {"timeline_candidates": timeline_candidates}
