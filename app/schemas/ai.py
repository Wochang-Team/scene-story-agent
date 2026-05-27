from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AssetForAnalysis(BaseModel):
    asset_id: UUID
    asset_type: str
    content_type: str
    object_key: str
    byte_size: int | None


class ImageForAnalysis(BaseModel):
    content_type: str
    data_base64: str


class SceneAnalysisInput(BaseModel):
    record_id: UUID
    memo: str | None
    emotion: str | None
    satisfaction_score: int | None
    happened_at: datetime | None
    assets: list[AssetForAnalysis]
    images: list[ImageForAnalysis]


class SceneAnalysisResult(BaseModel):
    provider: str
    model: str
    scene_type: str | None = None
    summary: str | None = None
    ocr_candidates: list[dict] = []
    place_candidates: list[dict] = []
    visit_time_candidates: list[dict] = []
    menu_candidates: list[dict] = []
    activity_candidates: list[dict] = []
    amount_candidates: list[dict] = []
    similar_record_candidates: list[dict] = []
    revisit_candidates: list[dict] = []
    timeline_candidates: list[dict] = []
    tags: list[str] = []
    raw_response_ref: dict | None = None


class SceneAnalysisResponse(BaseModel):
    interpretation_id: UUID
    record_id: UUID
    provider: str
    model: str
    scene_type: str | None
    summary: str | None
    ocr_candidates: list[dict] | None
    place_candidates: list[dict] | None
    visit_time_candidates: list[dict] | None
    menu_candidates: list[dict] | None
    activity_candidates: list[dict] | None
    amount_candidates: list[dict] | None
    similar_record_candidates: list[dict] | None
    revisit_candidates: list[dict] | None
    timeline_candidates: list[dict] | None
    tags: list[str] | None
    user_corrections: dict | None
    raw_response_ref: dict | None
    status: str
    created_at: datetime
    updated_at: datetime
