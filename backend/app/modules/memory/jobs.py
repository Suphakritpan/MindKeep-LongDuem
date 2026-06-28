"""Embed job handler (Batch F) — builds Work Memory from an approved document.

Enqueued by the review-before-memory approval flow (Batch G): a document only
reaches here after a reviewer with `memory:approve` approves it (ADR-008). The
embedding write-path lives in MemoryService.
"""
from sqlalchemy.orm import Session

from app.jobs.handlers import register
from app.jobs.models import Job
from app.modules.documents.models import Document
from app.modules.memory.service import MemoryService
from app.shared.enums import JobType


@register(JobType.embed)
def handle_embed(db: Session, job: Job) -> None:
    doc = db.get(Document, job.target_id)
    if doc is None:
        raise RuntimeError(f"document {job.target_id} not found")
    MemoryService(db).embed_document(doc, approved_by=job.created_by)
