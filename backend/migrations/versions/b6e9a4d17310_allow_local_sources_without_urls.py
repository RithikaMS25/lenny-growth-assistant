"""Allow local corpus records with no verified publisher URL.

Revision ID: b6e9a4d17310
Revises: afad8ccebe2b
"""
from alembic import op
import sqlalchemy as sa

revision = "b6e9a4d17310"
down_revision = "afad8ccebe2b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("sources", "url", existing_type=sa.Text(), nullable=True)


def downgrade() -> None:
    op.alter_column("sources", "url", existing_type=sa.Text(), nullable=False)
