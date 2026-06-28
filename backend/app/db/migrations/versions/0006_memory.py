"""create memory_entries, memory_chunks (Batch F)

Work Memory: knowledge promoted from a document after human approval (ADR-008),
chunked + embedded for permission-aware retrieval. The embedding is a pgvector
column on memory_chunks (ADR-006) — not a separate table. department_id and
visibility are denormalized onto chunks so permission filtering runs before the
vector search (ADR-007). The pgvector extension is enabled in migration 0001.

Revision ID: 0006_memory
Revises: 0005_document_extracted_text
Create Date: 2026-06-28
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "0006_memory"
down_revision: Union[str, None] = "0005_document_extracted_text"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UUID = postgresql.UUID(as_uuid=True)
_UUID_DEFAULT = sa.text("gen_random_uuid()")
_NOW = sa.text("now()")

# nomic-embed-text (settings.embedding_model) → 768 dims (mirrors memory.models.EMBEDDING_DIM)
_EMBEDDING_DIM = 768


def upgrade() -> None:
    op.create_table(
        "memory_entries",
        sa.Column("id", UUID, server_default=_UUID_DEFAULT, nullable=False),
        sa.Column("source_document_id", UUID, nullable=False),
        sa.Column("department_id", UUID, nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.Text()), server_default=sa.text("'{}'"), nullable=False),
        sa.Column("visibility", sa.String(32), server_default=sa.text("'private'"), nullable=False),
        sa.Column("created_by", UUID, nullable=False),
        sa.Column("approved_by", UUID, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_memory_entries"),
        sa.ForeignKeyConstraint(
            ["source_document_id"], ["documents.id"],
            name="fk_memory_entries_source_document_id_documents", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["department_id"], ["departments.id"],
            name="fk_memory_entries_department_id_departments",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name="fk_memory_entries_created_by_users"
        ),
        sa.ForeignKeyConstraint(
            ["approved_by"], ["users.id"], name="fk_memory_entries_approved_by_users"
        ),
    )
    op.create_index("ix_memory_entries_source_document_id", "memory_entries", ["source_document_id"])
    op.create_index("ix_memory_entries_department_id", "memory_entries", ["department_id"])

    op.create_table(
        "memory_chunks",
        sa.Column("id", UUID, server_default=_UUID_DEFAULT, nullable=False),
        sa.Column("memory_entry_id", UUID, nullable=False),
        sa.Column("department_id", UUID, nullable=False),
        sa.Column("visibility", sa.String(32), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(_EMBEDDING_DIM), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_memory_chunks"),
        sa.ForeignKeyConstraint(
            ["memory_entry_id"], ["memory_entries.id"],
            name="fk_memory_chunks_memory_entry_id_memory_entries", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["department_id"], ["departments.id"],
            name="fk_memory_chunks_department_id_departments",
        ),
    )
    op.create_index("ix_memory_chunks_memory_entry_id", "memory_chunks", ["memory_entry_id"])
    op.create_index("ix_memory_chunks_department_id", "memory_chunks", ["department_id"])
    # NOTE: the pgvector ANN index (ivfflat/hnsw) is added with retrieval in Batch H,
    # once the distance operator (cosine) and query path are settled.


def downgrade() -> None:
    op.drop_index("ix_memory_chunks_department_id", table_name="memory_chunks")
    op.drop_index("ix_memory_chunks_memory_entry_id", table_name="memory_chunks")
    op.drop_table("memory_chunks")
    op.drop_index("ix_memory_entries_department_id", table_name="memory_entries")
    op.drop_index("ix_memory_entries_source_document_id", table_name="memory_entries")
    op.drop_table("memory_entries")
