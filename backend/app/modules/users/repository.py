"""Data access for users + department membership."""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.users.models import User, UserDepartment


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, user_id: uuid.UUID) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def list(self, limit: int = 100, offset: int = 0) -> list[User]:
        stmt = select(User).order_by(User.created_at).limit(limit).offset(offset)
        return list(self.db.scalars(stmt))

    def add(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user

    def memberships(self, user_id: uuid.UUID) -> list[UserDepartment]:
        return list(self.db.scalars(select(UserDepartment).where(UserDepartment.user_id == user_id)))

    def active_department(self, user_id: uuid.UUID) -> uuid.UUID | None:
        memberships = self.memberships(user_id)
        if not memberships:
            return None
        for m in memberships:
            if m.is_active_default:
                return m.department_id
        return memberships[0].department_id
