"""Document business logic: notes, lifecycle, upload."""
import datetime as dt
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.jobs.repository import JobRepository
from app.modules.documents.models import Document, DocumentVersion, DocType
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.schemas import NoteCreate, NoteUpdate
from app.modules.files.models import File
from app.modules.files.repository import FileRepository
from app.modules.users.models import User
from app.shared.enums import DocState, DocVisibility, JobType
from app.storage.policy import MAX_UPLOAD_BYTES, is_allowed_extension, mime_for
from app.storage.service import StorageService


def _enqueue_extract(db, document_id, created_by) -> None:
    JobRepository(db).enqueue(
        type=JobType.extract,
        target_type="document",
        target_id=document_id,
        created_by=created_by,
    )


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class DocumentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = DocumentRepository(db)
        self.storage = StorageService()

    def create_note(self, user: User, payload: NoteCreate) -> Document:
        doc = Document(
            title=payload.title,
            doc_type=DocType.note,
            owner_id=user.id,
            department_id=payload.department_id,
            visibility=payload.visibility,
            state=DocState.draft,
        )
        self.repo.add(doc)
        self.repo.add_version(
            DocumentVersion(document_id=doc.id, version_no=1, content=payload.content, created_by=user.id)
        )
        _enqueue_extract(self.db, doc.id, user.id)
        self.db.commit()
        return doc

    def update_note(self, user: User, doc: Document, payload: NoteUpdate) -> Document:
        if doc.doc_type != DocType.note:
            raise AppError("documents.read_only", "Uploaded files are read-only in Phase 1", 422)
        data = payload.model_dump(exclude_unset=True)
        if "title" in data:
            doc.title = data["title"]
        if "visibility" in data:
            doc.visibility = data["visibility"]
        if "content" in data:
            # never overwrite — approved or not, content edits create a new version
            next_no = self.repo.latest_version_no(doc.id) + 1
            self.repo.add_version(
                DocumentVersion(
                    document_id=doc.id, version_no=next_no, content=data["content"], created_by=user.id
                )
            )
        self.db.commit()
        return doc

    def submit(self, doc: Document) -> Document:
        if doc.state not in (DocState.draft, DocState.rejected):
            raise AppError("documents.invalid_state", f"Cannot submit from {doc.state.value}", 409)
        doc.state = DocState.pending_review
        self.db.commit()
        return doc

    def set_lock(self, user: User, doc: Document, locked: bool) -> Document:
        doc.is_locked = locked
        doc.locked_by = user.id if locked else None
        doc.locked_at = _now() if locked else None
        self.db.commit()
        return doc

    def soft_delete(self, doc: Document) -> None:
        doc.deleted_at = _now()
        self.db.commit()

    def upload(
        self,
        user: User,
        *,
        title: str,
        department_id: uuid.UUID,
        visibility: DocVisibility,
        filename: str,
        data: bytes,
    ) -> tuple[Document, File]:
        ext = Path(filename).suffix
        if not is_allowed_extension(ext):
            raise AppError("documents.unsupported_type", f"Unsupported file type: {ext}", 422)
        if len(data) > MAX_UPLOAD_BYTES:
            raise AppError("documents.too_large", "File exceeds the 25MB limit", 413)

        stored = self.storage.save(data, str(department_id), filename)
        doc = Document(
            title=title,
            doc_type=DocType.uploaded,
            owner_id=user.id,
            department_id=department_id,
            visibility=visibility,
            state=DocState.draft,
        )
        self.repo.add(doc)
        file = FileRepository(self.db).add(
            File(
                document_id=doc.id,
                storage_path=stored.storage_path,
                original_filename=filename,
                mime_type=mime_for(ext),
                size_bytes=stored.size_bytes,
                checksum=stored.checksum,
                uploaded_by=user.id,
            )
        )
        _enqueue_extract(self.db, doc.id, user.id)
        self.db.commit()
        return doc, file
