"""enable pgvector extension

The vector extension is enabled here (not at app startup) so the DB schema is
fully reproducible from migrations. Subsequent batches add tables; memory_chunks
will use a vector column (Batch F).

Revision ID: 0001_enable_pgvector
Revises:
Create Date: 2026-06-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0001_enable_pgvector"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS vector")
