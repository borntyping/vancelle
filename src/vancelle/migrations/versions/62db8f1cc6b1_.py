"""empty message

Revision ID: 62db8f1cc6b1
Revises: bb59e6b6ad0b
Create Date: 2023-12-10 03:53:56.574435
"""

import alembic.op
import sqlalchemy


revision = "62db8f1cc6b1"
down_revision = "bb59e6b6ad0b"
branch_labels = None
depends_on = None


def upgrade():
    alembic.op.execute("CREATE COLLATION numeric (provider=icu, locale='en@colNumeric=yes');")
    with alembic.op.batch_alter_table("remote", schema=None) as batch_op:
        batch_op.alter_column(
            "id",
            existing_type=sqlalchemy.VARCHAR(),
            type_=sqlalchemy.Text(collation="numeric"),
            existing_nullable=False,
        )


def downgrade():
    with alembic.op.batch_alter_table("remote", schema=None) as batch_op:
        batch_op.alter_column(
            "id",
            existing_type=sqlalchemy.Text(collation="numeric"),
            type_=sqlalchemy.VARCHAR(),
            existing_nullable=False,
        )
    alembic.op.execute("DELETE COLLATION numeric;")
