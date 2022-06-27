"""add pyhon version

Revision ID: 3b00828b5d0b
Revises: 
Create Date: 2022-06-21 18:37:34.687391

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3b00828b5d0b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("session_context", sa.Column("python_version", sa.String))


def downgrade() -> None:
    op.drop_column("session_context", "python_version")
