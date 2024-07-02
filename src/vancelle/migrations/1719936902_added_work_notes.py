"""Added Work.notes

Revision ID: 1719936902
Revises: 1719394304
Create Date: 2024-07-02 17:15:03.019387
"""

import alembic.op
import sqlalchemy


revision = "1719936902"
down_revision = "1719394304"
branch_labels = ()
depends_on = None


def upgrade():
    alembic.op.add_column("work", sqlalchemy.Column("notes", sqlalchemy.String(), nullable=True))


def downgrade():
    alembic.op.drop_column("work", "notes")
