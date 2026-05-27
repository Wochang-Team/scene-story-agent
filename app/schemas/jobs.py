from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class JobResponse(BaseModel):
    job_id: UUID
    record_id: UUID
    job_type: str
    status: str
    cached_status: str | None = None
    attempt_count: int
    last_error_code: str | None
    last_error_message: str | None
    available_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime


class JobListResponse(BaseModel):
    jobs: list[JobResponse]


class JobClaimResponse(BaseModel):
    job: JobResponse | None
    lock_token: str | None


class JobFailureRequest(BaseModel):
    error_code: str = Field(min_length=1, max_length=80)
    error_message: str = Field(min_length=1, max_length=500)
    lock_token: str | None = None


class JobLockRequest(BaseModel):
    lock_token: str | None = None
