"""User business logic."""
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import hash_password
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserRepository(db)

    def create(self, payload: UserCreate) -> User:
        if self.repo.get_by_email(payload.email) is not None:
            raise AppError("users.duplicate_email", "Email already registered", 409)
        user = User(
            email=str(payload.email),
            password_hash=hash_password(payload.password),
            full_name=payload.full_name,
            phone=payload.phone,
            role=payload.role,
        )
        self.repo.add(user)
        self.db.commit()
        return user

    def update(self, user: User, payload: UserUpdate) -> User:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        self.db.commit()
        return user

    def deactivate(self, user: User) -> None:
        user.is_active = False
        self.db.commit()
