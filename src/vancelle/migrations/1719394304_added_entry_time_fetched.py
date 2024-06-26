"""Added Entry.time_fetched

Revision ID: 1719394304
Revises:
Create Date: 2024-06-26 10:31:44.219776
"""

import alembic.op
import sqlalchemy


revision = "1719394304"
down_revision = None
branch_labels = ("default",)
depends_on = None


def upgrade():
    alembic.op.add_column("remote", sqlalchemy.Column("time_fetched", sqlalchemy.DateTime(), nullable=True))


def downgrade():
    alembic.op.drop_column("remote", "time_fetched")
