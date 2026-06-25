"""Permission grant endpoints — manage capability grants (closes API_SPEC gap)."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.session import get_db
from app.modules.permissions.capabilities import ALL_CAPABILITIES, ROLES_MANAGE
from app.modules.permissions.models import PermissionGrant
from app.modules.permissions.repository import PermissionRepository
from app.modules.permissions.schemas import GrantCreate, GrantOut
from app.shared.deps import CurrentUser, require_capability

router = APIRouter()


@router.get("", response_model=list[GrantOut])
def list_grants(
    user_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_capability(ROLES_MANAGE))],
) -> list[PermissionGrant]:
    return PermissionRepository(db).list_for_user(user_id)


@router.post("", response_model=GrantOut, status_code=201)
def grant_capability(
    payload: GrantCreate,
    current: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_capability(ROLES_MANAGE))],
) -> PermissionGrant:
    if payload.capability not in ALL_CAPABILITIES:
        raise AppError("permissions.unknown_capability", f"Unknown capability: {payload.capability}", 422)
    grant = PermissionGrant(
        user_id=payload.user_id,
        capability=payload.capability,
        department_id=payload.department_id,
        granted_by=current.id,
    )
    PermissionRepository(db).add(grant)
    db.commit()
    return grant


@router.delete("/{grant_id}", status_code=204)
def revoke_capability(
    grant_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_capability(ROLES_MANAGE))],
) -> None:
    repo = PermissionRepository(db)
    grant = repo.get(grant_id)
    if grant is None:
        raise AppError("permissions.not_found", "Grant not found", 404)
    repo.delete(grant)
    db.commit()
