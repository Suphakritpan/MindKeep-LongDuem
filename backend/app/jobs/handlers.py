"""Job handler registry.

Later batches register handlers, e.g. (Batch E):
    @register(JobType.extract)
    def handle_extract(db, job): ...

The worker looks up a handler by job.type; a job with no registered handler
fails with a clear error (and respects retry limits).
"""
from collections.abc import Callable

from sqlalchemy.orm import Session

from app.jobs.models import Job
from app.shared.enums import JobType

JobHandler = Callable[[Session, Job], None]

HANDLERS: dict[JobType, JobHandler] = {}


def register(job_type: JobType) -> Callable[[JobHandler], JobHandler]:
    def _decorator(fn: JobHandler) -> JobHandler:
        HANDLERS[job_type] = fn
        return fn

    return _decorator


def get_handler(job_type: JobType) -> JobHandler | None:
    return HANDLERS.get(job_type)
