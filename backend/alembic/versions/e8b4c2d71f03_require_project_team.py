"""require project team

Revision ID: e8b4c2d71f03
Revises: d5f3a8c61e29
Create Date: 2026-11-10 16:40:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e8b4c2d71f03"
down_revision: str | Sequence[str] | None = "d5f3a8c61e29"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Projects created before teams existed have no team and are unreachable.
    # Their tasks, comments, labels and activity go with them via ON DELETE CASCADE.
    op.execute("DELETE FROM projects WHERE team_id IS NULL")
    op.alter_column("projects", "team_id", existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    op.alter_column("projects", "team_id", existing_type=sa.Integer(), nullable=True)
