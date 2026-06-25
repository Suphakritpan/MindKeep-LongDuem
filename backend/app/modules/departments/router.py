"""Department endpoints."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.session import get_db
from app.modules.departments.models import Department
from app.modules.departments.repository import DepartmentRepository
from app.modules.departments.schemas import DepartmentCreate, DepartmentOut
from app.modules.permissions.capabilities import DEPARTMENTS_MANAGE
from app.shared.deps import CurrentUser, require_capability

router = APIRouter()


@router.get("", response_model=list[DepartmentOut])
def list_departments(_: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> list[Department]:
    return DepartmentRepository(db).list()


@router.get("/{department_id}", response_model=DepartmentOut)
def get_department(
    department_id: uuid.UUID, _: CurrentUser, db: Annotated[Session, Depends(get_db)]
) -> Department:
    dept = DepartmentRepository(db).get(department_id)
    if dept is None:
        raise AppError("departments.not_found", "Department not found", 404)
    return dept


@router.post("", response_model=DepartmentOut, status_code=201)
def create_department(
    payload: DepartmentCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_capability(DEPARTMENTS_MANAGE))],
) -> Department:
    repo = DepartmentRepository(db)
    if repo.get_by_key(payload.key) is not None:
        raise AppError("departments.duplicate_key", f"Department key already exists: {payload.key}", 409)
    dept = repo.add(Department(key=payload.key, name=payload.name, description=payload.description))
    db.commit()
    return dept
