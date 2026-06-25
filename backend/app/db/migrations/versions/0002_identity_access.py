"""create identity & access tables (Batch B)

Tables: departments, users, user_departments, permission_grants.
Role columns are VARCHAR(32) (ADR-018: enums stored as strings; validated at the
ORM/Pydantic layer via app.shared.enums.Role).

Revision ID: 0002_identity_access
Revises: 0001_enable_pgvector
Create Date: 2026-06-25
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_identity_access"
down_revision: Union[str, None] = "0001_enable_pgvector"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UUID = postgresql.UUID(as_uuid=True)
_UUID_DEFAULT = sa.text("gen_random_uuid()")
_NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", UUID, server_default=_UUID_DEFAULT, nullable=False),
        sa.Column("key", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_departments"),
    )
    op.create_index("ix_departments_key", "departments", ["key"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", UUID, server_default=_UUID_DEFAULT, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("avatar_url", sa.String(512), nullable=True),
        sa.Column("role", sa.String(32), server_default=sa.text("'employee'"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "user_departments",
        sa.Column("id", UUID, server_default=_UUID_DEFAULT, nullable=False),
        sa.Column("user_id", UUID, nullable=False),
        sa.Column("department_id", UUID, nullable=False),
        sa.Column("role_in_department", sa.String(32), server_default=sa.text("'employee'"), nullable=False),
        sa.Column("is_active_default", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_user_departments"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_user_departments_user_id_users", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["department_id"], ["departments.id"],
            name="fk_user_departments_department_id_departments", ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "user_id", "department_id", name="uq_user_departments_user_id_department_id"
        ),
    )
    op.create_index("ix_user_departments_user_id", "user_departments", ["user_id"])
    op.create_index("ix_user_departments_department_id", "user_departments", ["department_id"])

    op.create_table(
        "permission_grants",
        sa.Column("id", UUID, server_default=_UUID_DEFAULT, nullable=False),
        sa.Column("user_id", UUID, nullable=False),
        sa.Column("capability", sa.String(64), nullable=False),
        sa.Column("department_id", UUID, nullable=True),
        sa.Column("granted_by", UUID, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_permission_grants"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_permission_grants_user_id_users", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["department_id"], ["departments.id"],
            name="fk_permission_grants_department_id_departments", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["granted_by"], ["users.id"], name="fk_permission_grants_granted_by_users"
        ),
    )
    op.create_index("ix_permission_grants_user_id", "permission_grants", ["user_id"])
    op.create_index("ix_permission_grants_capability", "permission_grants", ["capability"])


def downgrade() -> None:
    op.drop_table("permission_grants")
    op.drop_table("user_departments")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_departments_key", table_name="departments")
    op.drop_table("departments")
