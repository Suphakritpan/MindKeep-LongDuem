"""Permission grant schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GrantCreate(BaseModel):
    user_id: uuid.UUID
    capability: str
    department_id: uuid.UUID | None = None


class GrantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    capability: str
    department_id: uuid.UUID | None
    granted_by: uuid.UUID
    created_at: datetime
