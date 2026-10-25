"""create teams

Revision ID: b7d2f1a90c44
Revises: a1c8e4b27d10
Create Date: 2026-10-26 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7d2f1a90c44"
down_revision: Union[str, Sequence[str], None] = "a1c8e4b27d10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "team_members",
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("team_id", "user_id"),
    )
    op.add_column("projects", sa.Column("team_id", sa.Integer(), nullable=True))
    op.create_index("ix_projects_team_id", "projects", ["team_id"])
    op.create_foreign_key(
        "fk_projects_team_id_teams",
        "projects",
        "teams",
        ["team_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_projects_team_id_teams", "projects", type_="foreignkey")
    op.drop_index("ix_projects_team_id", table_name="projects")
    op.drop_column("projects", "team_id")
    op.drop_table("team_members")
    op.drop_table("teams")
