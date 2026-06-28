"""Work Memory business logic — build embedded memory from an approved document.

A document only reaches `embed_document` after human approval (ADR-008); the
approval flow (Batch G) enqueues the `embed` job. Re-embedding replaces the
entry's chunks (append-only chunks => delete + insert) so retrieval never sees a
half-updated set.
"""
import datetime as dt
import uuid

from sqlalchemy.orm import Session

from app.jobs.repository import JobRepository
from app.modules.ai.embeddings import EmbeddingClient
from app.modules.documents.models import Document
from app.modules.memory.chunking import chunk_text
from app.modules.memory.models import MemoryChunk, MemoryEntry
from app.modules.memory.repository import MemoryRepository
from app.shared.enums import DocVisibility, JobType, MemVisibility


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _mem_visibility_for(doc_vis: DocVisibility) -> MemVisibility:
    """DocVisibility's four values map 1:1 to MemVisibility. `shared_knowledge`
    is never derived from a document (ADR-010) — it needs a separate promotion
    with `shared_knowledge:approve`."""
    return MemVisibility(doc_vis.value)


class MemoryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = MemoryRepository(db)
        self.embedder = EmbeddingClient()

    def enqueue_embed(self, document_id: uuid.UUID, approved_by: uuid.UUID | None) -> None:
        """Queue the embed job. Called by the approval flow (Batch G) once a
        document becomes approved_to_memory — never on plain upload."""
        JobRepository(self.db).enqueue(
            type=JobType.embed,
            target_type="document",
            target_id=document_id,
            created_by=approved_by,
        )

    def embed_document(self, doc: Document, *, approved_by: uuid.UUID | None) -> MemoryEntry:
        chunks_text = chunk_text((doc.extracted_text or "").strip())
        if not chunks_text:
            raise RuntimeError(f"document {doc.id} has no extracted_text to embed")

        visibility = _mem_visibility_for(doc.visibility)

        entry = self.repo.entry_for_document(doc.id)
        if entry is None:
            entry = self.repo.add_entry(
                MemoryEntry(
                    source_document_id=doc.id,
                    department_id=doc.department_id,
                    summary=doc.summary,
                    visibility=visibility,
                    created_by=doc.owner_id,
                    approved_by=approved_by,
                    approved_at=_now(),
                )
            )
        else:  # re-embed: refresh entry + replace its chunks
            entry.summary = doc.summary
            entry.visibility = visibility
            entry.approved_by = approved_by
            entry.approved_at = _now()
            self.repo.delete_chunks(entry.id)

        vectors = self.embedder.embed_batch(chunks_text)
        self.repo.add_chunks(
            [
                MemoryChunk(
                    memory_entry_id=entry.id,
                    department_id=doc.department_id,
                    visibility=visibility,
                    chunk_index=i,
                    content=content,
                    embedding=vector,
                )
                for i, (content, vector) in enumerate(zip(chunks_text, vectors))
            ]
        )
        self.db.commit()
        return entry
