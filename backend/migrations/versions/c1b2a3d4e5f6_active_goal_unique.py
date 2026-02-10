"""enforce single active goal per user

Revision ID: c1b2a3d4e5f6
Revises: dcd649568149
Create Date: 2026-02-09 23:05:00.000000
"""
from __future__ import annotations

from alembic import op


revision = "c1b2a3d4e5f6"
down_revision = "dcd649568149"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_goals_user_active")
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                user_id,
                ROW_NUMBER() OVER (
                    PARTITION BY user_id
                    ORDER BY created_at DESC, id DESC
                ) AS rn
            FROM goals
            WHERE is_active = 1
        )
        UPDATE goals
        SET is_active = 0
        WHERE id IN (SELECT id FROM ranked WHERE rn > 1);
        """
    )
    dialect = op.get_bind().dialect.name
    where_sql = "is_active = 1" if dialect == "sqlite" else "is_active IS TRUE"
    op.execute(
        f"CREATE UNIQUE INDEX IF NOT EXISTS uq_goals_active_per_user ON goals(user_id) WHERE {where_sql};"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_goals_active_per_user")
    dialect = op.get_bind().dialect.name
    where_sql = "is_active = 1" if dialect == "sqlite" else "is_active IS TRUE"
    op.execute(
        f"CREATE UNIQUE INDEX IF NOT EXISTS ix_goals_user_active ON goals(user_id) WHERE {where_sql};"
    )
