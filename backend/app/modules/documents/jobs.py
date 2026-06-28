"""Document processing job handlers (Batch E).

The `extract` job pulls text from the source (file or note content), stores it on
the document, and generates a summary via the local LLM (with fallback). Embedding
into Work Memory happens later, only after human approval (Batch F/G).
"""
from sqlalchemy.orm import Session

from app.jobs.handlers import register
from app.jobs.models import Job
from app.modules.ai.llm import OllamaClient
from app.modules.documents.extraction import extract_text
from app.modules.documents.models import DocType, Document
from app.modules.documents.repository import DocumentRepository
from app.modules.files.repository import FileRepository
from app.shared.enums import JobType
from app.storage.service import StorageService


@register(JobType.extract)
def handle_extract(db: Session, job: Job) -> None:
    doc = db.get(Document, job.target_id)
    if doc is None:
        raise RuntimeError(f"document {job.target_id} not found")

    if doc.doc_type == DocType.note:
        versions = DocumentRepository(db).versions(doc.id)
        text = (versions[0].content or "") if versions else ""
    else:
        file = FileRepository(db).by_document(doc.id)
        if file is None:
            raise RuntimeError(f"no file attached to document {doc.id}")
        text = extract_text(StorageService().read(file.storage_path), file.original_filename)

    doc.extracted_text = text or None
    doc.summary = OllamaClient().summarize(text)
    db.commit()
