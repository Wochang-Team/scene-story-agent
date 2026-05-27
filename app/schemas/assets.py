from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AssetResponse(BaseModel):
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


class AssetListResponse(BaseModel):
    assets: list[AssetResponse]
