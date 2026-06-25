"""Document endpoints — notes, lifecycle, upload/download (Batch C)."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File as UploadFileMarker, Form, Response, UploadFile
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.session import get_db
from app.modules.documents.models import Document
from app.modules.documents.permissions import can_edit, can_manage_lock, can_view
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.schemas import DocumentOut, NoteCreate, NoteUpdate, VersionOut
from app.modules.documents.service import DocumentService
from app.modules.files.repository import FileRepository
from app.modules.permissions.service import PermissionService
from app.modules.users.models import User
from app.shared.deps import CurrentUser
from app.shared.enums import DocVisibility, Role
from app.storage.service import StorageService

router = APIRouter()

DbDep = Annotated[Session, Depends(get_db)]


def _load(db: Session, document_id: uuid.UUID) -> Document:
    doc = DocumentRepository(db).get(document_id)
    if doc is None:
        raise AppError("documents.not_found", "Document not found", 404)
    return doc


def _require_member(perm: PermissionService, user: User, department_id: uuid.UUID) -> None:
    if user.role == Role.owner_manager:
        return
    if department_id not in perm.department_ids(user):
        raise AppError("documents.forbidden_department", "Not a member of this department", 403)


@router.post("", response_model=DocumentOut, status_code=201)
def create_note(payload: NoteCreate, current: CurrentUser, db: DbDep) -> Document:
    _require_member(PermissionService(db), current, payload.department_id)
    return DocumentService(db).create_note(current, payload)


@router.get("", response_model=list[DocumentOut])
def list_documents(current: CurrentUser, db: DbDep, limit: int = 100, offset: int = 0) -> list[Document]:
    allowed = PermissionService(db).allowed_departments(current)
    return DocumentRepository(db).list_visible(current.id, allowed, limit=limit, offset=offset)


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: uuid.UUID, current: CurrentUser, db: DbDep) -> Document:
    doc = _load(db, document_id)
    if not can_view(PermissionService(db), current, doc):
        raise AppError("documents.forbidden", "No access to this document", 403)
    return doc


@router.patch("/{document_id}", response_model=DocumentOut)
def update_document(
    document_id: uuid.UUID, payload: NoteUpdate, current: CurrentUser, db: DbDep
) -> Document:
    doc = _load(db, document_id)
    if not can_edit(current, doc):
        raise AppError("documents.forbidden_edit", "Cannot edit (not owner, locked, or deleted)", 403)
    return DocumentService(db).update_note(current, doc, payload)


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: uuid.UUID, current: CurrentUser, db: DbDep) -> None:
    doc = _load(db, document_id)
    if doc.deleted_at is not None:
        return
    perm = PermissionService(db)
    owner_unlocked = doc.owner_id == current.id and not doc.is_locked
    if not (owner_unlocked or can_manage_lock(perm, current, doc)):
        raise AppError("documents.forbidden_delete", "Cannot delete this document", 403)
    DocumentService(db).soft_delete(doc)


@router.post("/{document_id}/submit", response_model=DocumentOut)
def submit_document(document_id: uuid.UUID, current: CurrentUser, db: DbDep) -> Document:
    doc = _load(db, document_id)
    if doc.owner_id != current.id and current.role != Role.owner_manager:
        raise AppError("documents.forbidden", "Only the owner can submit", 403)
    return DocumentService(db).submit(doc)


@router.post("/{document_id}/lock", response_model=DocumentOut)
def lock_document(document_id: uuid.UUID, current: CurrentUser, db: DbDep) -> Document:
    doc = _load(db, document_id)
    if not can_manage_lock(PermissionService(db), current, doc):
        raise AppError("documents.forbidden_lock", "Only a department lead can lock", 403)
    return DocumentService(db).set_lock(current, doc, True)


@router.post("/{document_id}/unlock", response_model=DocumentOut)
def unlock_document(document_id: uuid.UUID, current: CurrentUser, db: DbDep) -> Document:
    doc = _load(db, document_id)
    if not can_manage_lock(PermissionService(db), current, doc):
        raise AppError("documents.forbidden_lock", "Only a department lead can unlock", 403)
    return DocumentService(db).set_lock(current, doc, False)


@router.get("/{document_id}/versions", response_model=list[VersionOut])
def list_versions(document_id: uuid.UUID, current: CurrentUser, db: DbDep) -> list:
    doc = _load(db, document_id)
    if not can_view(PermissionService(db), current, doc):
        raise AppError("documents.forbidden", "No access to this document", 403)
    return DocumentRepository(db).versions(document_id)


@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload_document(
    current: CurrentUser,
    db: DbDep,
    title: Annotated[str, Form()],
    department_id: Annotated[uuid.UUID, Form()],
    file: Annotated[UploadFile, UploadFileMarker()],
    visibility: Annotated[DocVisibility, Form()] = DocVisibility.private,
) -> Document:
    _require_member(PermissionService(db), current, department_id)
    data = await file.read()
    doc, _ = DocumentService(db).upload(
        current,
        title=title,
        department_id=department_id,
        visibility=visibility,
        filename=file.filename or "upload",
        data=data,
    )
    return doc


@router.get("/{document_id}/download")
def download_document(document_id: uuid.UUID, current: CurrentUser, db: DbDep) -> Response:
    doc = _load(db, document_id)
    if not can_view(PermissionService(db), current, doc):
        raise AppError("documents.forbidden", "No access to this document", 403)
    file = FileRepository(db).by_document(document_id)
    if file is None:
        raise AppError("documents.no_file", "No file attached to this document", 404)
    data = StorageService().read(file.storage_path)
    return Response(
        content=data,
        media_type=file.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{file.original_filename}"'},
    )
