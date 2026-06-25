"""Auth endpoints: login, me, logout."""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.schemas import (
    LoginRequest,
    MembershipOut,
    MeResponse,
    MeUpdate,
    TokenResponse,
)
from app.modules.auth.service import AuthService
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.shared.deps import CurrentUser

router = APIRouter()


def _build_me(user: User, db: Session) -> MeResponse:
    repo = UserRepository(db)
    memberships = repo.memberships(user.id)
    return MeResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        avatar_url=user.avatar_url,
        role=user.role,
        is_active=user.is_active,
        active_department_id=repo.active_department(user.id),
        departments=[MembershipOut.model_validate(m) for m in memberships],
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    svc = AuthService(db)
    user = svc.authenticate(str(payload.email), payload.password)
    return TokenResponse(access_token=svc.issue_token(user))


@router.get("/me", response_model=MeResponse)
def me(current: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> MeResponse:
    return _build_me(current, db)


@router.patch("/me", response_model=MeResponse)
def update_me(
    payload: MeUpdate, current: CurrentUser, db: Annotated[Session, Depends(get_db)]
) -> MeResponse:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current, field, value)
    db.commit()
    return _build_me(current, db)


@router.post("/logout", status_code=204)
def logout(_: CurrentUser) -> None:
    # Stateless JWT — client discards the token. Server-side revocation is future work.
    return None
