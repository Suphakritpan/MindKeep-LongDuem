"""Import all modules that register job handlers, so the worker sees them.

Each import has the side effect of running its @register(...) decorators.
"""
# Batch E — document extraction + summary
from app.modules.documents import jobs as _document_jobs  # noqa: F401

# Batch F — work memory embedding
from app.modules.memory import jobs as _memory_jobs  # noqa: F401
