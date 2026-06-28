"""Data access for Work Memory entries + chunks."""
import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.modules.memory.models import MemoryChunk, MemoryEntry


class MemoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def entry_for_document(self, document_id: uuid.UUID) -> MemoryEntry | None:
        stmt = select(MemoryEntry).where(MemoryEntry.source_document_id == document_id)
        return self.db.scalars(stmt).first()

    def add_entry(self, entry: MemoryEntry) -> MemoryEntry:
        self.db.add(entry)
        self.db.flush()
        return entry

    def delete_chunks(self, memory_entry_id: uuid.UUID) -> None:
        self.db.execute(delete(MemoryChunk).where(MemoryChunk.memory_entry_id == memory_entry_id))

    def add_chunks(self, chunks: list[MemoryChunk]) -> None:
        self.db.add_all(chunks)
        self.db.flush()
