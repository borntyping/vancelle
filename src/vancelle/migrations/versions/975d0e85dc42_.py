"""Make 'work.shelf' a required field.

Revision ID: 975d0e85dc42
Revises: 62db8f1cc6b1
Create Date: 2023-12-10 04:40:59.709567
"""

import alembic.op
import sqlalchemy


revision = "975d0e85dc42"
down_revision = "62db8f1cc6b1"
branch_labels = None
depends_on = None


def upgrade():
    with alembic.op.batch_alter_table("work", schema=None) as batch_op:
        batch_op.alter_column("shelf", existing_type=sqlalchemy.VARCHAR(length=10), nullable=False)


def downgrade():
    with alembic.op.batch_alter_table("work", schema=None) as batch_op:
        batch_op.alter_column("shelf", existing_type=sqlalchemy.VARCHAR(length=10), nullable=True)
