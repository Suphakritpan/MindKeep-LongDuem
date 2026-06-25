"""Background job model — durable queue (ADR-012, ADR-025)."""
import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.shared.enums import JobStatus, JobType


def _enum(enum_cls: type, length: int) -> SAEnum:
    return SAEnum(enum_cls, native_enum=False, length=length, validate_strings=True)


class Job(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "jobs"

    type: Mapped[JobType] = mapped_column(_enum(JobType, 32), index=True)
    status: Mapped[JobStatus] = mapped_column(
        _enum(JobStatus, 16), default=JobStatus.queued, nullable=False, index=True
    )
    target_type: Mapped[str] = mapped_column(String(64))  # e.g. "document", "file"
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
