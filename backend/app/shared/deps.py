"""Shared FastAPI dependencies: current user + capability guard."""
import uuid
from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import decode_token
from app.db.session import get_db
from app.modules.permissions.service import PermissionService
from app.modules.users.models import User
from app.modules.users.repository import UserRepository

_bearer = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    try:
        payload = decode_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise AppError("auth.invalid_token", "Invalid or expired token", 401) from exc

    sub = payload.get("sub")
    if not sub:
        raise AppError("auth.invalid_token", "Token missing subject", 401)

    user = UserRepository(db).get(uuid.UUID(sub))
    if user is None or not user.is_active:
        raise AppError("auth.inactive_user", "User not found or inactive", 401)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_capability(capability: str) -> Callable[..., User]:
    """Dependency factory: 403 unless the current user holds `capability` (global scope)."""

    def _dep(user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> User:
        if not PermissionService(db).has_capability(user, capability):
            raise AppError("auth.forbidden", f"Missing capability: {capability}", 403)
        return user

    return _dep
