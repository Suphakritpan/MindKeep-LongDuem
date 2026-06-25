"""File endpoints — list own, download (with parent-doc access), delete."""
import datetime as dt
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.session import get_db
from app.modules.documents.permissions import can_view
from app.modules.documents.repository import DocumentRepository
from app.modules.files.models import File
from app.modules.files.repository import FileRepository
from app.modules.files.schemas import FileOut
from app.modules.permissions.service import PermissionService
from app.shared.deps import CurrentUser
from app.shared.enums import Role
from app.storage.service import StorageService

router = APIRouter()

DbDep = Annotated[Session, Depends(get_db)]


def _load(db: Session, file_id: uuid.UUID) -> File:
    file = FileRepository(db).get(file_id)
    if file is None or file.deleted_at is not None:
        raise AppError("files.not_found", "File not found", 404)
    return file


@router.get("", response_model=list[FileOut])
def list_my_files(current: CurrentUser, db: DbDep) -> list[File]:
    return FileRepository(db).list_for_uploader(current.id)


@router.get("/{file_id}/download")
def download_file(file_id: uuid.UUID, current: CurrentUser, db: DbDep) -> Response:
    file = _load(db, file_id)
    # access via parent document if attached; otherwise uploader-only
    if file.document_id is not None:
        doc = DocumentRepository(db).get(file.document_id)
        if doc is None or not can_view(PermissionService(db), current, doc):
            raise AppError("files.forbidden", "No access to this file", 403)
    elif file.uploaded_by != current.id and current.role != Role.owner_manager:
        raise AppError("files.forbidden", "No access to this file", 403)

    data = StorageService().read(file.storage_path)
    return Response(
        content=data,
        media_type=file.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{file.original_filename}"'},
    )


@router.delete("/{file_id}", status_code=204)
def delete_file(file_id: uuid.UUID, current: CurrentUser, db: DbDep) -> None:
    file = _load(db, file_id)
    if file.uploaded_by != current.id and current.role != Role.owner_manager:
        raise AppError("files.forbidden_delete", "Cannot delete this file", 403)
    file.deleted_at = dt.datetime.now(dt.timezone.utc)
    StorageService().delete(file.storage_path)
    db.commit()
