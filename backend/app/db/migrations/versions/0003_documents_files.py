"""create documents, document_versions, files (Batch C)

Revision ID: 0003_documents_files
Revises: 0002_identity_access
Create Date: 2026-06-25
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_documents_files"
down_revision: Union[str, None] = "0002_identity_access"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UUID = postgresql.UUID(as_uuid=True)
_UUID_DEFAULT = sa.text("gen_random_uuid()")
_NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", UUID, server_default=_UUID_DEFAULT, nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("doc_type", sa.String(16), server_default=sa.text("'note'"), nullable=False),
        sa.Column("owner_id", UUID, nullable=False),
        sa.Column("department_id", UUID, nullable=False),
        sa.Column("visibility", sa.String(32), server_default=sa.text("'private'"), nullable=False),
        sa.Column("state", sa.String(32), server_default=sa.text("'draft'"), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("is_locked", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("locked_by", UUID, nullable=True),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_documents"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], name="fk_documents_owner_id_users"),
        sa.ForeignKeyConstraint(
            ["department_id"], ["departments.id"], name="fk_documents_department_id_departments"
        ),
        sa.ForeignKeyConstraint(["locked_by"], ["users.id"], name="fk_documents_locked_by_users"),
    )
    op.create_index("ix_documents_owner_id", "documents", ["owner_id"])
    op.create_index("ix_documents_department_id", "documents", ["department_id"])

    op.create_table(
        "document_versions",
        sa.Column("id", UUID, server_default=_UUID_DEFAULT, nullable=False),
        sa.Column("document_id", UUID, nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("created_by", UUID, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_document_versions"),
        sa.ForeignKeyConstraint(
            ["document_id"], ["documents.id"],
            name="fk_document_versions_document_id_documents", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name="fk_document_versions_created_by_users"
        ),
        sa.UniqueConstraint(
            "document_id", "version_no", name="uq_document_versions_document_id_version_no"
        ),
    )
    op.create_index("ix_document_versions_document_id", "document_versions", ["document_id"])

    op.create_table(
        "files",
        sa.Column("id", UUID, server_default=_UUID_DEFAULT, nullable=False),
        sa.Column("document_id", UUID, nullable=True),
        sa.Column("storage_path", sa.String(1024), nullable=False),
        sa.Column("original_filename", sa.String(512), nullable=False),
        sa.Column("mime_type", sa.String(255), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("uploaded_by", UUID, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_files"),
        sa.ForeignKeyConstraint(
            ["document_id"], ["documents.id"], name="fk_files_document_id_documents", ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], name="fk_files_uploaded_by_users"),
    )
    op.create_index("ix_files_document_id", "files", ["document_id"])
    op.create_index("ix_files_checksum", "files", ["checksum"])


def downgrade() -> None:
    op.drop_table("files")
    op.drop_index("ix_document_versions_document_id", table_name="document_versions")
    op.drop_table("document_versions")
    op.drop_index("ix_documents_department_id", table_name="documents")
    op.drop_index("ix_documents_owner_id", table_name="documents")
    op.drop_table("documents")
