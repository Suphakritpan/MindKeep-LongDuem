"""Auth schemas."""
import uuid

from pydantic import BaseModel, ConfigDict, EmailStr

from app.shared.enums import Role


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MembershipOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    department_id: uuid.UUID
    role_in_department: Role
    is_active_default: bool


class MeResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    phone: str | None
    avatar_url: str | None
    role: Role
    is_active: bool
    active_department_id: uuid.UUID | None
    departments: list[MembershipOut]


class MeUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
