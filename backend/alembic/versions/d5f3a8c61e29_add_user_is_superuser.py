"""add user is_superuser

Revision ID: d5f3a8c61e29
Revises: c3a91e7b52d8
Create Date: 2026-10-31 07:10:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d5f3a8c61e29"
down_revision: str | Sequence[str] | None = "c3a91e7b52d8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("users", "is_superuser")
