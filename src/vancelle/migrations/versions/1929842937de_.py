"""Add 'series' to Work and Remote.

Revision ID: 1929842937de
Revises: a6073baccc99
Create Date: 2024-01-24 13:26:29.563885
"""

import alembic.op
import sqlalchemy


revision = "1929842937de"
down_revision = "a6073baccc99"
branch_labels = None
depends_on = None


def upgrade():
    with alembic.op.batch_alter_table("remote", schema=None) as batch_op:
        batch_op.add_column(sqlalchemy.Column("series", sqlalchemy.String(), nullable=True))

    with alembic.op.batch_alter_table("work", schema=None) as batch_op:
        batch_op.add_column(sqlalchemy.Column("series", sqlalchemy.String(), nullable=True))


def downgrade():
    with alembic.op.batch_alter_table("work", schema=None) as batch_op:
        batch_op.drop_column("series")

    with alembic.op.batch_alter_table("remote", schema=None) as batch_op:
        batch_op.drop_column("series")
