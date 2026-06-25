"""Document schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modules.documents.models import DocType
from app.shared.enums import DocState, DocVisibility


class NoteCreate(BaseModel):
    title: str
    content: str = ""
    department_id: uuid.UUID
    visibility: DocVisibility = DocVisibility.private


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    visibility: DocVisibility | None = None


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    doc_type: DocType
    owner_id: uuid.UUID
    department_id: uuid.UUID
    visibility: DocVisibility
    state: DocState
    summary: str | None
    is_locked: bool
    created_at: datetime
    updated_at: datetime


class VersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    version_no: int
    content: str | None
    created_by: uuid.UUID
    created_at: datetime
