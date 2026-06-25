"""Data access for permission grants + department membership lookups."""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.permissions.models import PermissionGrant
from app.modules.users.models import UserDepartment


class PermissionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # --- grants ---
    def grants_for(self, user_id: uuid.UUID, capability: str) -> list[PermissionGrant]:
        stmt = select(PermissionGrant).where(
            PermissionGrant.user_id == user_id, PermissionGrant.capability == capability
        )
        return list(self.db.scalars(stmt))

    def list_for_user(self, user_id: uuid.UUID) -> list[PermissionGrant]:
        return list(self.db.scalars(select(PermissionGrant).where(PermissionGrant.user_id == user_id)))

    def get(self, grant_id: uuid.UUID) -> PermissionGrant | None:
        return self.db.get(PermissionGrant, grant_id)

    def add(self, grant: PermissionGrant) -> PermissionGrant:
        self.db.add(grant)
        self.db.flush()
        return grant

    def delete(self, grant: PermissionGrant) -> None:
        self.db.delete(grant)

    # --- membership ---
    def memberships(self, user_id: uuid.UUID) -> list[UserDepartment]:
        return list(self.db.scalars(select(UserDepartment).where(UserDepartment.user_id == user_id)))
