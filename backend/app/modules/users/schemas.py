"""User schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.shared.enums import Role


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: str | None = None
    role: Role = Role.employee


class UserUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    role: Role | None = None
    is_active: bool | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    phone: str | None
    avatar_url: str | None
    role: Role
    is_active: bool
    created_at: datetime
