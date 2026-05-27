from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RecordCreate(BaseModel):
    memo: str | None = None
    emotion: str | None = None
    satisfaction_score: int | None = Field(default=None, ge=1, le=5)
    happened_at: datetime | None = None


class RecordUpdate(BaseModel):
    memo: str | None = None
    emotion: str | None = None
    satisfaction_score: int | None = Field(default=None, ge=1, le=5)
    happened_at: datetime | None = None


class RecordResponse(BaseModel):
    record_id: UUID
    user_id: UUID
    memo: str | None
    emotion: str | None
    satisfaction_score: int | None
    happened_at: datetime | None
    status: str
    created_at: datetime
    updated_at: datetime


class RecordListResponse(BaseModel):
    records: list[RecordResponse]
