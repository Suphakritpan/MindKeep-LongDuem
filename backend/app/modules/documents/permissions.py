"""Document access checks — built on the central PermissionService."""
from app.modules.documents.models import Document
from app.modules.permissions.service import PermissionService
from app.modules.users.models import User
from app.shared.enums import DocVisibility, Role


def can_view(perm: PermissionService, user: User, doc: Document) -> bool:
    if doc.deleted_at is not None:
        return user.role == Role.owner_manager or doc.owner_id == user.id
    if user.role == Role.owner_manager or doc.owner_id == user.id:
        return True
    if doc.visibility == DocVisibility.public_internal:
        return True
    if doc.visibility == DocVisibility.department:
        return doc.department_id in perm.department_ids(user)
    # private / restricted → owner (or owner_manager) only
    return False


def can_edit(user: User, doc: Document) -> bool:
    """Owner edits their own doc while it is unlocked and not deleted."""
    if doc.deleted_at is not None or doc.is_locked:
        return False
    return doc.owner_id == user.id


def can_manage_lock(perm: PermissionService, user: User, doc: Document) -> bool:
    """Lock/unlock + delete-of-others = department_lead of the doc's dept, or owner_manager."""
    if user.role == Role.owner_manager:
        return True
    return perm.is_department_lead(user, doc.department_id)
