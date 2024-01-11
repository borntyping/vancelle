"""empty message

Revision ID: a6073baccc99
Revises: 975d0e85dc42
Create Date: 2024-01-11 18:31:50.837664
"""

import alembic.op
import sqlalchemy


revision = "a6073baccc99"
down_revision = "975d0e85dc42"
branch_labels = None
depends_on = None


def upgrade():
    with alembic.op.batch_alter_table("work", schema=None) as batch_op:
        batch_op.add_column(sqlalchemy.Column("external_url", sqlalchemy.String(), nullable=True))


def downgrade():
    with alembic.op.batch_alter_table("work", schema=None) as batch_op:
        batch_op.drop_column("external_url")
