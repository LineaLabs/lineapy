"""create account table

Revision ID: 79c3440c8214
Revises: 
Create Date: 2022-06-21 16:22:20.456114

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "79c3440c8214"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "account",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("description", sa.Unicode(200)),
    )


def downgrade() -> None:
    op.drop_table("account")
