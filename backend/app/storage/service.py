"""StorageService — local filesystem first, MinIO/S3 later (ADR-011).

All file IO goes through here so the backend can be swapped without touching
business code. Path layout: <department_key>/<uuid><ext> under STORAGE_LOCAL_PATH.
"""
import hashlib
import uuid
from dataclasses import dataclass
from pathlib import Path

from app.core.config import settings


@dataclass(frozen=True)
class StoredFile:
    storage_path: str  # relative to the storage root, POSIX-style
    checksum: str  # sha256 hex
    size_bytes: int


class StorageService:
    def __init__(self, base_path: str | None = None) -> None:
        self.base = Path(base_path or settings.storage_local_path)

    def save(self, data: bytes, department_key: str, original_filename: str) -> StoredFile:
        ext = Path(original_filename).suffix
        rel = f"{department_key}/{uuid.uuid4().hex}{ext}"
        dest = self.base / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return StoredFile(
            storage_path=rel,
            checksum=hashlib.sha256(data).hexdigest(),
            size_bytes=len(data),
        )

    def read(self, storage_path: str) -> bytes:
        return (self.base / storage_path).read_bytes()

    def delete(self, storage_path: str) -> None:
        target = self.base / storage_path
        if target.exists():
            target.unlink()
