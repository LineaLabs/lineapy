"""Add a column

Revision ID: 68ba4e0dd1dd
Revises: 79c3440c8214
Create Date: 2022-06-21 16:46:13.492048

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "68ba4e0dd1dd"
down_revision = "79c3440c8214"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("account", sa.Column("last_transaction_date", sa.DateTime))


def downgrade() -> None:
    op.drop_column("account", "last_transaction_date")
