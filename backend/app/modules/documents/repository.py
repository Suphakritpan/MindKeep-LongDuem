"""Data access for documents + versions."""
import uuid
from collections.abc import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.modules.documents.models import Document, DocumentVersion
from app.shared.enums import DocVisibility


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, document_id: uuid.UUID) -> Document | None:
        return self.db.get(Document, document_id)

    def add(self, document: Document) -> Document:
        self.db.add(document)
        self.db.flush()
        return document

    def list_visible(
        self,
        user_id: uuid.UUID,
        allowed_department_ids: Sequence[uuid.UUID] | None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Document]:
        """allowed_department_ids None => owner/manager (see all non-deleted)."""
        stmt = select(Document).where(Document.deleted_at.is_(None))
        if allowed_department_ids is not None:
            stmt = stmt.where(
                or_(
                    Document.owner_id == user_id,
                    Document.visibility == DocVisibility.public_internal,
                    (Document.visibility == DocVisibility.department)
                    & Document.department_id.in_(allowed_department_ids),
                )
            )
        stmt = stmt.order_by(Document.created_at.desc()).limit(limit).offset(offset)
        return list(self.db.scalars(stmt))

    # --- versions ---
    def latest_version_no(self, document_id: uuid.UUID) -> int:
        stmt = select(func.coalesce(func.max(DocumentVersion.version_no), 0)).where(
            DocumentVersion.document_id == document_id
        )
        return int(self.db.scalar(stmt) or 0)

    def add_version(self, version: DocumentVersion) -> DocumentVersion:
        self.db.add(version)
        self.db.flush()
        return version

    def versions(self, document_id: uuid.UUID) -> list[DocumentVersion]:
        stmt = (
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_no.desc())
        )
        return list(self.db.scalars(stmt))
