"""Aggregate /api/v1 router."""
from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.departments.router import router as departments_router
from app.modules.documents.router import router as documents_router
from app.jobs.router import router as jobs_router
from app.modules.files.router import router as files_router
from app.modules.permissions.router import router as permissions_router
from app.modules.users.router import router as users_router

api_router = APIRouter()

# Batch B — identity & access
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(departments_router, prefix="/departments", tags=["departments"])
api_router.include_router(permissions_router, prefix="/permissions", tags=["permissions"])

# Batch C — documents & files
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_router.include_router(files_router, prefix="/files", tags=["files"])

# Batch D — background jobs
api_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])

# Later batches: memory, ai, chat, activities, audit
