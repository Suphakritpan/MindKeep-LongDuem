"""Shared enums — single source of truth, mirrors docs/DATA_MODEL.md §0.

Stored as VARCHAR (SQLAlchemy Enum(native_enum=False)) so values can evolve
across phases without a Postgres ALTER TYPE migration.
"""
from enum import Enum


class Role(str, Enum):
    employee = "employee"
    department_lead = "department_lead"
    owner_manager = "owner_manager"


class DocVisibility(str, Enum):
    """Visibility allowed on documents/files (no shared_knowledge)."""

    private = "private"
    department = "department"
    public_internal = "public_internal"
    restricted = "restricted"


class MemVisibility(str, Enum):
    """Visibility on memory_entries/memory_chunks — adds shared_knowledge (post-approval)."""

    private = "private"
    department = "department"
    public_internal = "public_internal"
    restricted = "restricted"
    shared_knowledge = "shared_knowledge"


class DocState(str, Enum):
    """Review lifecycle only. Lock/delete are flags, not states (see DATA_MODEL §0)."""

    draft = "draft"
    pending_review = "pending_review"
    approved_to_memory = "approved_to_memory"
    rejected = "rejected"


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class JobType(str, Enum):
    extract = "extract"
    ocr = "ocr"
    preview = "preview"
    summary = "summary"
    embed = "embed"
    reembed = "reembed"
    ai_postprocess = "ai_postprocess"


class ActivityStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    locked = "locked"
