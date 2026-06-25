"""Job status endpoints — list / inspect / retry (processing visibility)."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.session import get_db
from app.jobs.models import Job
from app.jobs.repository import JobRepository
from app.jobs.schemas import JobOut
from app.modules.permissions.capabilities import AUDIT_VIEW
from app.modules.permissions.service import PermissionService
from app.modules.users.models import User
from app.shared.deps import CurrentUser
from app.shared.enums import JobStatus, Role

router = APIRouter()

DbDep = Annotated[Session, Depends(get_db)]


def _is_admin_view(perm: PermissionService, user: User) -> bool:
    return user.role == Role.owner_manager or perm.has_capability(user, AUDIT_VIEW)


@router.get("", response_model=list[JobOut])
def list_jobs(current: CurrentUser, db: DbDep, limit: int = 100, offset: int = 0) -> list[Job]:
    scope = None if _is_admin_view(PermissionService(db), current) else current.id
    return JobRepository(db).list(scope, limit=limit, offset=offset)


def _load_authorized(db: Session, current: User, job_id: uuid.UUID) -> Job:
    job = JobRepository(db).get(job_id)
    if job is None:
        raise AppError("jobs.not_found", "Job not found", 404)
    if not _is_admin_view(PermissionService(db), current) and job.created_by != current.id:
        raise AppError("jobs.forbidden", "No access to this job", 403)
    return job


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: uuid.UUID, current: CurrentUser, db: DbDep) -> Job:
    return _load_authorized(db, current, job_id)


@router.post("/{job_id}/retry", response_model=JobOut)
def retry_job(job_id: uuid.UUID, current: CurrentUser, db: DbDep) -> Job:
    job = _load_authorized(db, current, job_id)
    if job.status != JobStatus.failed:
        raise AppError(
            "jobs.not_retryable", f"Only failed jobs can be retried (status={job.status.value})", 409
        )
    return JobRepository(db).requeue(job)
