"""Import all SQLAlchemy models so Alembic autogenerate sees them via Base.metadata.

Add module models here as each batch introduces them.
"""
from app.db.base import Base  # noqa: F401  (re-export so env.py has metadata)

# Batch B — identity & access
from app.modules.departments import models as _departments  # noqa: F401
from app.modules.users import models as _users  # noqa: F401
from app.modules.permissions import models as _permissions  # noqa: F401

# Batch C — documents & files
from app.modules.documents import models as _documents  # noqa: F401
from app.modules.files import models as _files  # noqa: F401

# Batch D — background jobs
from app.jobs import models as _jobs  # noqa: F401

# Batch F — work memory + embeddings
from app.modules.memory import models as _memory  # noqa: F401
