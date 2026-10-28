"""add task reporter and assignee

Revision ID: a1c8e4b27d10
Revises: 790e33a24b5a
Create Date: 2026-10-26 01:56:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a1c8e4b27d10"
down_revision: str | Sequence[str] | None = "790e33a24b5a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("reporter_id", sa.Integer(), nullable=True))
    op.add_column("tasks", sa.Column("assignee_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_tasks_reporter_id_users",
        "tasks",
        "users",
        ["reporter_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_tasks_assignee_id_users",
        "tasks",
        "users",
        ["assignee_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_tasks_assignee_id_users", "tasks", type_="foreignkey")
    op.drop_constraint("fk_tasks_reporter_id_users", "tasks", type_="foreignkey")
    op.drop_column("tasks", "assignee_id")
    op.drop_column("tasks", "reporter_id")
