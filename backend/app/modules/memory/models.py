"""Work Memory models — approved knowledge + embedded chunks (Batch F).

`memory_entries` hold knowledge promoted from a document AFTER human approval
(ADR-008). `memory_chunks` store the chunked text + a pgvector embedding used for
permission-aware retrieval (ADR-006/007). Both are append-only: re-embedding a
document replaces its chunks rather than mutating them — so there is no
`updated_at`, only `created_at`.
"""
import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, Text, func, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKeyMixin
from app.shared.enums import MemVisibility

# nomic-embed-text (settings.embedding_model) produces 768-dim vectors. The DB
# column dimension is fixed; changing the embed model implies a re-embed migration.
EMBEDDING_DIM = 768


def _enum(enum_cls: type, length: int) -> SAEnum:
    return SAEnum(enum_cls, native_enum=False, length=length, validate_strings=True)


class MemoryEntry(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "memory_entries"

    source_document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id"), index=True
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default=text("'{}'"), nullable=False)
    # Defaults to the most restrictive value; the embed handler sets it explicitly
    # from the source document's visibility. `shared_knowledge` is only reachable
    # via a separate promotion that requires `shared_knowledge:approve` (ADR-010).
    visibility: Mapped[MemVisibility] = mapped_column(
        _enum(MemVisibility, 32), default=MemVisibility.private, nullable=False
    )
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MemoryChunk(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "memory_chunks"

    memory_entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("memory_entries.id", ondelete="CASCADE"), index=True
    )
    # department_id + visibility are denormalized from the entry so permission
    # filtering runs BEFORE the vector search (ADR-007) without a join.
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id"), index=True
    )
    visibility: Mapped[MemVisibility] = mapped_column(_enum(MemVisibility, 32), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
