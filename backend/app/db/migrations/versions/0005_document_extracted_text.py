"""add documents.extracted_text (Batch E)

Stores the text pulled from the source file/note so a reviewer can compare it with
the summary before approval (review-before-memory, Batch G).

Revision ID: 0005_document_extracted_text
Revises: 0004_jobs
Create Date: 2026-06-25
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_document_extracted_text"
down_revision: Union[str, None] = "0004_jobs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("extracted_text", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("documents", "extracted_text")
