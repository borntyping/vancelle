import logging

import alembic
import flask

from vancelle.models import Base
from vancelle.extensions import db

logger = logging.getLogger("alembic.env")


def run_migrations_offline():
    alembic.context.configure(url=db.engine.url, target_metadata=Base.metadata, literal_binds=True)
    with alembic.context.begin_transaction():
        alembic.context.run_migrations()


def run_migrations_online():
    with db.engine.connect() as connection:
        config = flask.current_app.extensions["migrate"]
        alembic.context.configure(connection=connection, target_metadata=Base.metadata, **config.configure_args)
        with alembic.context.begin_transaction():
            alembic.context.run_migrations()


if alembic.context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
