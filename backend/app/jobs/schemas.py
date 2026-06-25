"""Job schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.shared.enums import JobStatus, JobType


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: JobType
    status: JobStatus
    target_type: str
    target_id: uuid.UUID
    attempts: int
    max_attempts: int
    error: str | None
    created_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
