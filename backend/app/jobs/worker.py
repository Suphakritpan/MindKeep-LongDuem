"""Background worker — polls the jobs table and runs registered handlers.

Run:  python -m app.jobs.worker
A heavy task creates a Job row; this loop claims and executes it outside the
request cycle (ADR-012). Safe to run multiple workers (FOR UPDATE SKIP LOCKED).
"""
import logging
import time

import app.jobs.loader  # noqa: F401 — registers handlers from later batches
from app.db.session import SessionLocal
from app.jobs.handlers import get_handler
from app.jobs.repository import JobRepository

logger = logging.getLogger("mindkeep.worker")
POLL_INTERVAL_SECONDS = 2.0


def run_once() -> bool:
    """Claim and run at most one job. Returns True if a job was processed."""
    db = SessionLocal()
    try:
        repo = JobRepository(db)
        job = repo.claim_next()
        if job is None:
            return False
        handler = get_handler(job.type)
        try:
            if handler is None:
                raise RuntimeError(f"No handler registered for job type '{job.type.value}'")
            handler(db, job)
            repo.mark_succeeded(job)
            logger.info("job %s (%s) succeeded", job.id, job.type.value)
        except Exception as exc:  # noqa: BLE001 — the worker must not die on a bad job
            # discard any partial writes from the failed handler before recording status
            db.rollback()
            repo.mark_failed_or_retry(job, str(exc))
            logger.warning("job %s (%s) failed: %s", job.id, job.type.value, exc)
        return True
    finally:
        db.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger.info("MindKeep worker started (poll=%.1fs)", POLL_INTERVAL_SECONDS)
    while True:
        if not run_once():
            time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
