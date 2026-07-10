"""add verdict column to evaluation_runs

Revision ID: 0002_add_verdict
Revises: 0001_initial
Create Date: 2026-07-08

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_add_verdict"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "evaluation_runs",
        sa.Column("verdict", sa.String(length=16), nullable=True),
    )
    op.create_index("ix_evaluation_runs_verdict", "evaluation_runs", ["verdict"])


def downgrade() -> None:
    op.drop_index("ix_evaluation_runs_verdict", table_name="evaluation_runs")
    op.drop_column("evaluation_runs", "verdict")
