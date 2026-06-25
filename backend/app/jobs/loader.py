"""Import all modules that register job handlers, so the worker sees them.

Later batches add imports here, e.g. (Batch E):
    from app.modules.documents import jobs as _doc_jobs  # noqa: F401

Batch D has no handlers yet.
"""
