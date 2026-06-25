"""Data access for files."""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.files.models import File


class FileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, file_id: uuid.UUID) -> File | None:
        return self.db.get(File, file_id)

    def by_document(self, document_id: uuid.UUID) -> File | None:
        stmt = (
            select(File)
            .where(File.document_id == document_id, File.deleted_at.is_(None))
            .order_by(File.created_at.desc())
        )
        return self.db.scalars(stmt).first()

    def list_for_uploader(self, user_id: uuid.UUID) -> list[File]:
        stmt = (
            select(File)
            .where(File.uploaded_by == user_id, File.deleted_at.is_(None))
            .order_by(File.created_at.desc())
        )
        return list(self.db.scalars(stmt))

    def add(self, file: File) -> File:
        self.db.add(file)
        self.db.flush()
        return file
