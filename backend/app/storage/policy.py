"""Upload policy — supported file types (docs/SCOPE.md §3) + size limit."""

# extension -> mime type (Phase 1 supported set)
ALLOWED_TYPES: dict[str, str] = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".csv": "text/csv",
}

MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MB


def is_allowed_extension(ext: str) -> bool:
    return ext.lower() in ALLOWED_TYPES


def mime_for(ext: str) -> str:
    return ALLOWED_TYPES.get(ext.lower(), "application/octet-stream")
