"""empty message

Revision ID: bb59e6b6ad0b
Revises:
Create Date: 2023-12-09 18:33:28.672494
"""

import alembic.op
import sqlalchemy
from sqlalchemy.dialects import postgresql

revision = "bb59e6b6ad0b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    alembic.op.create_table(
        "steam_appids",
        sqlalchemy.Column("appid", sqlalchemy.Integer(), nullable=False),
        sqlalchemy.Column("name", sqlalchemy.String(), nullable=False),
        sqlalchemy.PrimaryKeyConstraint("appid"),
    )
    alembic.op.create_table(
        "user",
        sqlalchemy.Column("id", sqlalchemy.Uuid(), nullable=False),
        sqlalchemy.Column("username", sqlalchemy.String(), nullable=False),
        sqlalchemy.Column("password", sqlalchemy.String(), nullable=False),
        sqlalchemy.PrimaryKeyConstraint("id"),
        sqlalchemy.UniqueConstraint("username"),
    )
    alembic.op.create_table(
        "work",
        sqlalchemy.Column("user_id", sqlalchemy.Uuid(), nullable=False),
        sqlalchemy.Column("id", sqlalchemy.Uuid(), nullable=False),
        sqlalchemy.Column("type", sqlalchemy.String(), nullable=False),
        sqlalchemy.Column("time_created", sqlalchemy.DateTime(), nullable=False),
        sqlalchemy.Column("time_updated", sqlalchemy.DateTime(), nullable=True),
        sqlalchemy.Column("time_deleted", sqlalchemy.DateTime(), nullable=True),
        sqlalchemy.Column("title", sqlalchemy.String(), nullable=True),
        sqlalchemy.Column("author", sqlalchemy.String(), nullable=True),
        sqlalchemy.Column("description", sqlalchemy.String(), nullable=True),
        sqlalchemy.Column("release_date", sqlalchemy.Date(), nullable=True),
        sqlalchemy.Column("cover", sqlalchemy.String(), nullable=True),
        sqlalchemy.Column("background", sqlalchemy.String(), nullable=True),
        sqlalchemy.Column(
            "shelf",
            sqlalchemy.Enum(
                "unsorted",
                "unreleased",
                "undecided",
                "upcoming",
                "playing",
                "replaying",
                "ongoing",
                "infinite",
                "paused",
                "shelved",
                "reference",
                "completed",
                "abandoned",
                name="shelf",
                native_enum=False,
            ),
            nullable=True,
        ),
        sqlalchemy.Column("tags", postgresql.ARRAY(sqlalchemy.String()), nullable=True),
        sqlalchemy.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sqlalchemy.PrimaryKeyConstraint("id"),
    )
    alembic.op.create_table(
        "record",
        sqlalchemy.Column("work_id", sqlalchemy.Uuid(), nullable=False),
        sqlalchemy.Column("id", sqlalchemy.Uuid(), nullable=False),
        sqlalchemy.Column("time_created", sqlalchemy.DateTime(), nullable=False),
        sqlalchemy.Column("time_updated", sqlalchemy.DateTime(), nullable=True),
        sqlalchemy.Column("time_deleted", sqlalchemy.DateTime(), nullable=True),
        sqlalchemy.Column("date_started", sqlalchemy.Date(), nullable=True),
        sqlalchemy.Column("date_stopped", sqlalchemy.Date(), nullable=True),
        sqlalchemy.Column("notes", sqlalchemy.String(), nullable=True),
        sqlalchemy.ForeignKeyConstraint(["work_id"], ["work.id"], ondelete="CASCADE"),
        sqlalchemy.PrimaryKeyConstraint("id"),
    )
    alembic.op.create_table(
        "remote",
        sqlalchemy.Column("work_id", sqlalchemy.Uuid(), nullable=False),
        sqlalchemy.Column("type", sqlalchemy.String(), nullable=False),
        sqlalchemy.Column("time_created", sqlalchemy.DateTime(), nullable=False),
        sqlalchemy.Column("time_updated", sqlalchemy.DateTime(), nullable=True),
        sqlalchemy.Column("time_deleted", sqlalchemy.DateTime(), nullable=True),
        sqlalchemy.Column("id", sqlalchemy.String(), nullable=False),
        sqlalchemy.Column("title", sqlalchemy.String(), nullable=True),
        sqlalchemy.Column("author", sqlalchemy.String(), nullable=True),
        sqlalchemy.Column("description", sqlalchemy.String(), nullable=True),
        sqlalchemy.Column("release_date", sqlalchemy.Date(), nullable=True),
        sqlalchemy.Column("cover", sqlalchemy.String(), nullable=True),
        sqlalchemy.Column("background", sqlalchemy.String(), nullable=True),
        sqlalchemy.Column(
            "shelf",
            sqlalchemy.Enum(
                "unsorted",
                "unreleased",
                "undecided",
                "upcoming",
                "playing",
                "replaying",
                "ongoing",
                "infinite",
                "paused",
                "shelved",
                "reference",
                "completed",
                "abandoned",
                name="shelf",
                native_enum=False,
            ),
            nullable=True,
        ),
        sqlalchemy.Column("tags", postgresql.ARRAY(sqlalchemy.String()), nullable=True),
        sqlalchemy.Column("data", postgresql.JSONB(astext_type=sqlalchemy.Text()), nullable=True),
        sqlalchemy.ForeignKeyConstraint(["work_id"], ["work.id"], ondelete="cascade"),
        sqlalchemy.PrimaryKeyConstraint("type", "id"),
    )


def downgrade():
    alembic.op.drop_table("remote")
    alembic.op.drop_table("record")
    alembic.op.drop_table("work")
    alembic.op.drop_table("user")
    alembic.op.drop_table("steam_appids")
