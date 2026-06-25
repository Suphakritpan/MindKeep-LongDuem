"""Capability constants (mirrors docs/DATA_MODEL.md §permission_grants)."""

# System / admin
USERS_MANAGE = "users:manage"
DEPARTMENTS_MANAGE = "departments:manage"
ROLES_MANAGE = "roles:manage"
SYSTEM_SETTINGS = "system:settings"
AUDIT_VIEW = "audit:view"

# Memory / knowledge
MEMORY_APPROVE = "memory:approve"
SHARED_KNOWLEDGE_APPROVE = "shared_knowledge:approve"

# Finance (Phase 2 — listed for completeness)
FINANCE_OCR_USE = "finance:ocr_use"
FINANCE_RECORD_SUBMIT = "finance:record_submit"
FINANCE_RECORD_CONFIRM = "finance:record_confirm"
FINANCE_RECORD_POST = "finance:record_post"
FINANCE_SUMMARY_VIEW = "finance:summary_view"
FINANCE_SETTINGS_MANAGE = "finance:settings_manage"

ALL_CAPABILITIES = frozenset(
    {
        USERS_MANAGE,
        DEPARTMENTS_MANAGE,
        ROLES_MANAGE,
        SYSTEM_SETTINGS,
        AUDIT_VIEW,
        MEMORY_APPROVE,
        SHARED_KNOWLEDGE_APPROVE,
        FINANCE_OCR_USE,
        FINANCE_RECORD_SUBMIT,
        FINANCE_RECORD_CONFIRM,
        FINANCE_RECORD_POST,
        FINANCE_SUMMARY_VIEW,
        FINANCE_SETTINGS_MANAGE,
    }
)

# Capabilities a department_lead holds implicitly *within their own department*.
DEPARTMENT_LEAD_IMPLICIT = frozenset({MEMORY_APPROVE})
