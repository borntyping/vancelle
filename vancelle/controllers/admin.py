import typing

import pydantic
import requests
import requests_cache
import sqlalchemy
import structlog

from vancelle.extensions import db
from vancelle.models import Base

logger = structlog.get_logger(logger_name=__name__)


class AdminController:
    def create_database(self):
        logger.info("Creating database")
        db.session.execute(sqlalchemy.sql.text("CREATE EXTENSION IF NOT EXISTS isn;"))
        db.session.execute(sqlalchemy.sql.text("CREATE EXTENSION IF NOT EXISTS hstore;"))
        db.session.commit()
        db.create_all()
        logger.info("Created database")

    def drop_database(self):
        logger.critical("Dropping database")
        db.drop_all()
        logger.critical("Dropped database")

    def clear_request_cache():
        session = requests.Session()
        if isinstance(session, requests_cache.CachedSession):
            logger.warning("Clearing requests cache")
            session.cache.clear()
