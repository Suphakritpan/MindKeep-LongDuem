"""User management endpoints (capability: users:manage)."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.session import get_db
from app.modules.permissions.capabilities import USERS_MANAGE
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserOut, UserUpdate
from app.modules.users.service import UserService
from app.shared.deps import require_capability

router = APIRouter()

ManageDep = Annotated[object, Depends(require_capability(USERS_MANAGE))]


@router.get("", response_model=list[UserOut])
def list_users(
    db: Annotated[Session, Depends(get_db)], _: ManageDep, limit: int = 100, offset: int = 0
) -> list[User]:
    return UserRepository(db).list(limit=limit, offset=offset)


@router.post("", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Annotated[Session, Depends(get_db)], _: ManageDep) -> User:
    return UserService(db).create(payload)


def _get_or_404(db: Session, user_id: uuid.UUID) -> User:
    user = UserRepository(db).get(user_id)
    if user is None:
        raise AppError("users.not_found", "User not found", 404)
    return user


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: uuid.UUID, db: Annotated[Session, Depends(get_db)], _: ManageDep) -> User:
    return _get_or_404(db, user_id)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: uuid.UUID, payload: UserUpdate, db: Annotated[Session, Depends(get_db)], _: ManageDep
) -> User:
    return UserService(db).update(_get_or_404(db, user_id), payload)


@router.post("/{user_id}/deactivate", status_code=204)
def deactivate_user(
    user_id: uuid.UUID, db: Annotated[Session, Depends(get_db)], _: ManageDep
) -> None:
    UserService(db).deactivate(_get_or_404(db, user_id))
