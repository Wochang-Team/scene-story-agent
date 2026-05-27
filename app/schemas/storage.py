from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel

FIELD_CONTRACT = {
    "app_users": [
        "user_id",
        "auth_provider",
        "auth_subject",
        "email",
        "display_name",
        "created_at",
        "updated_at",
        "deleted_at",
    ],
    "records": [
        "record_id",
        "user_id",
        "memo",
        "emotion",
        "satisfaction_score",
        "happened_at",
        "status",
        "created_at",
        "updated_at",
        "deleted_at",
    ],
    "record_assets": [
        "asset_id",
        "record_id",
        "asset_type",
        "storage_provider",
        "bucket_name",
        "object_key",
        "content_type",
        "byte_size",
        "width",
        "height",
        "duration_seconds",
        "checksum_sha256",
        "created_at",
        "deleted_at",
    ],
    "record_ai_interpretations": [
        "interpretation_id",
        "record_id",
        "provider",
        "model",
        "scene_type",
        "summary",
        "ocr_candidates",
        "place_candidates",
        "visit_time_candidates",
        "menu_candidates",
        "activity_candidates",
        "amount_candidates",
        "similar_record_candidates",
        "revisit_candidates",
        "timeline_candidates",
        "tags",
        "user_corrections",
        "raw_response_ref",
        "status",
        "created_at",
        "updated_at",
        "deleted_at",
    ],
    "record_embeddings": [
        "embedding_id",
        "record_id",
        "provider",
        "model",
        "dimension",
        "embedding",
        "input_snapshot",
        "created_at",
        "deleted_at",
    ],
    "record_relations": [
        "relation_id",
        "source_record_id",
        "target_record_id",
        "relation_type",
        "similarity_score",
        "decision_status",
        "reasons",
        "created_at",
        "updated_at",
    ],
    "timeline_candidates": [
        "timeline_candidate_id",
        "user_id",
        "record_id",
        "timeline_type",
        "grouping_key",
        "confidence_score",
        "reasons",
        "created_at",
    ],
    "processing_jobs": [
        "job_id",
        "record_id",
        "job_type",
        "status",
        "attempt_count",
        "last_error_code",
        "last_error_message",
        "available_at",
        "started_at",
        "finished_at",
        "created_at",
        "updated_at",
    ],
}


class StoredUser(BaseModel):
    user_id: UUID
    auth_provider: str
    auth_subject: str
    email: str | None
    display_name: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class StoredRecord(BaseModel):
    record_id: UUID
    user_id: UUID
    memo: str | None
    emotion: str | None
    satisfaction_score: int | None
    happened_at: datetime | None
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class StoredAsset(BaseModel):
    asset_id: UUID
    record_id: UUID
    asset_type: str
    storage_provider: str
    bucket_name: str
    object_key: str
    content_type: str
    byte_size: int | None
    width: int | None
    height: int | None
    duration_seconds: int | None
    checksum_sha256: str | None
    created_at: datetime
    deleted_at: datetime | None


class StoredAIInterpretation(BaseModel):
    interpretation_id: UUID
    record_id: UUID
    provider: str
    model: str
    scene_type: str | None
    summary: str | None
    ocr_candidates: list[dict[str, Any]] | None
    place_candidates: list[dict[str, Any]] | None
    visit_time_candidates: list[dict[str, Any]] | None
    menu_candidates: list[dict[str, Any]] | None
    activity_candidates: list[dict[str, Any]] | None
    amount_candidates: list[dict[str, Any]] | None
    similar_record_candidates: list[dict[str, Any]] | None
    revisit_candidates: list[dict[str, Any]] | None
    timeline_candidates: list[dict[str, Any]] | None
    tags: list[str] | None
    user_corrections: dict[str, Any] | None
    raw_response_ref: dict[str, Any] | None
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class StoredEmbedding(BaseModel):
    embedding_id: UUID
    record_id: UUID
    provider: str
    model: str
    dimension: int
    embedding: str
    input_snapshot: dict[str, Any]
    created_at: datetime
    deleted_at: datetime | None


class StoredRelation(BaseModel):
    relation_id: UUID
    source_record_id: UUID
    target_record_id: UUID
    relation_type: str
    similarity_score: Decimal | None
    decision_status: str
    reasons: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime


class StoredTimelineCandidate(BaseModel):
    timeline_candidate_id: UUID
    user_id: UUID
    record_id: UUID
    timeline_type: str
    grouping_key: str
    confidence_score: Decimal | None
    reasons: dict[str, Any] | None
    created_at: datetime


class StoredProcessingJob(BaseModel):
    job_id: UUID
    record_id: UUID
    job_type: str
    status: str
    attempt_count: int
    last_error_code: str | None
    last_error_message: str | None
    available_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime


class StorageExportData(BaseModel):
    app_users: StoredUser
    records: StoredRecord
    record_assets: list[StoredAsset]
    record_ai_interpretations: list[StoredAIInterpretation]
    record_embeddings: list[StoredEmbedding]
    record_relations: list[StoredRelation]
    timeline_candidates: list[StoredTimelineCandidate]
    processing_jobs: list[StoredProcessingJob]


class StorageExportResponse(BaseModel):
    field_contract: dict[str, list[str]]
    data: StorageExportData
