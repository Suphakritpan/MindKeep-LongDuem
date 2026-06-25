"""Auth business logic: authenticate + issue token."""
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import create_access_token, verify_password
from app.modules.users.models import User
from app.modules.users.repository import UserRepository


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def authenticate(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email)
        if user is None or not user.is_active or not verify_password(password, user.password_hash):
            raise AppError("auth.invalid_credentials", "Invalid email or password", 401)
        return user

    def issue_token(self, user: User) -> str:
        return create_access_token(str(user.id), {"role": user.role.value})
