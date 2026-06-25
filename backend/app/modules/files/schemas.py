"""File schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID | None
    original_filename: str
    mime_type: str
    size_bytes: int
    checksum: str
    uploaded_by: uuid.UUID
    created_at: datetime
