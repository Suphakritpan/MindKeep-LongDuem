"""Central permission service — the single place backend authorization is decided.

This is the foundation of "permission before retrieval" (ADR-007): documents,
memory and AI/RAG resolve access here BEFORE any query runs.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from app.modules.permissions.capabilities import DEPARTMENT_LEAD_IMPLICIT
from app.modules.permissions.repository import PermissionRepository
from app.shared.enums import Role

if TYPE_CHECKING:
    from app.modules.users.models import User


class PermissionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = PermissionRepository(db)

    def has_capability(
        self, user: "User", capability: str, department_id: uuid.UUID | None = None
    ) -> bool:
        # owner/manager has org-wide management authority (cross-dept access is audited).
        if user.role == Role.owner_manager:
            return True

        # department_lead holds a few capabilities implicitly within their own department.
        if (
            capability in DEPARTMENT_LEAD_IMPLICIT
            and department_id is not None
            and self.is_department_lead(user, department_id)
        ):
            return True

        # explicit grants — global (department_id is NULL) or matching the target department.
        for grant in self.repo.grants_for(user.id, capability):
            if grant.department_id is None or grant.department_id == department_id:
                return True
        return False

    def is_department_lead(self, user: "User", department_id: uuid.UUID) -> bool:
        for m in self.repo.memberships(user.id):
            if m.department_id == department_id and m.role_in_department == Role.department_lead:
                return True
        return False

    def department_ids(self, user: "User") -> list[uuid.UUID]:
        """Departments a user is a member of."""
        return [m.department_id for m in self.repo.memberships(user.id)]

    def allowed_departments(self, user: "User") -> list[uuid.UUID] | None:
        """Departments whose data the user may access.

        Returns None to mean "all departments" (owner/manager). Callers must still
        choose an explicit scope for AI retrieval — never default to all silently.
        """
        if user.role == Role.owner_manager:
            return None
        return self.department_ids(user)
