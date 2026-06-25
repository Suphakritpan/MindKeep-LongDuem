"""Data access + state transitions for background jobs."""
import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.jobs.models import Job
from app.shared.enums import JobStatus, JobType

_ERROR_MAX = 2000


class JobRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def enqueue(
        self,
        *,
        type: JobType,
        target_type: str,
        target_id: uuid.UUID,
        created_by: uuid.UUID | None = None,
        payload: dict | None = None,
        max_attempts: int = 3,
    ) -> Job:
        job = Job(
            type=type,
            status=JobStatus.queued,
            target_type=target_type,
            target_id=target_id,
            created_by=created_by,
            payload=payload,
            max_attempts=max_attempts,
        )
        self.db.add(job)
        self.db.flush()
        return job

    def get(self, job_id: uuid.UUID) -> Job | None:
        return self.db.get(Job, job_id)

    def list(
        self, created_by: uuid.UUID | None, limit: int = 100, offset: int = 0
    ) -> list[Job]:
        """created_by None => no scope filter (admin view)."""
        stmt = select(Job).order_by(Job.created_at.desc()).limit(limit).offset(offset)
        if created_by is not None:
            stmt = stmt.where(Job.created_by == created_by)
        return list(self.db.scalars(stmt))

    def claim_next(self) -> Job | None:
        """Atomically claim one queued job (concurrency-safe across workers)."""
        stmt = (
            select(Job)
            .where(Job.status == JobStatus.queued)
            .order_by(Job.created_at)
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        job = self.db.scalars(stmt).first()
        if job is None:
            return None
        job.status = JobStatus.running
        job.attempts += 1
        self.db.commit()
        self.db.refresh(job)
        return job

    def mark_succeeded(self, job: Job) -> None:
        job.status = JobStatus.succeeded
        job.error = None
        self.db.commit()

    def mark_failed_or_retry(self, job: Job, error: str) -> None:
        job.error = error[:_ERROR_MAX]
        job.status = JobStatus.failed if job.attempts >= job.max_attempts else JobStatus.queued
        self.db.commit()

    def requeue(self, job: Job) -> Job:
        job.status = JobStatus.queued
        job.attempts = 0
        job.error = None
        self.db.commit()
        return job
