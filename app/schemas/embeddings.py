from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class EmbeddingResponse(BaseModel):
    embedding_id: UUID
    record_id: UUID
    provider: str
    model: str
    dimension: int
    input_snapshot: dict
    created_at: datetime


class RelationResponse(BaseModel):
    relation_id: UUID
    source_record_id: UUID
    target_record_id: UUID
    relation_type: str
    similarity_score: Decimal | None
    decision_status: str
    reasons: dict | None
    created_at: datetime
    updated_at: datetime


class TimelineCandidateResponse(BaseModel):
    timeline_candidate_id: UUID
    user_id: UUID
    record_id: UUID
    timeline_type: str
    grouping_key: str
    confidence_score: Decimal | None
    reasons: dict | None
    created_at: datetime


class EmbeddingBuildResponse(BaseModel):
    embedding: EmbeddingResponse
    relations: list[RelationResponse]
    timeline_candidates: list[TimelineCandidateResponse]


class RelationListResponse(BaseModel):
    relations: list[RelationResponse]


class TimelineCandidateListResponse(BaseModel):
    timeline_candidates: list[TimelineCandidateResponse]
