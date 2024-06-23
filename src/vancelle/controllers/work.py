import dataclasses
import datetime
import uuid

import flask_login
import sqlalchemy
import structlog
from sqlalchemy.orm import joinedload
from sqlalchemy import select

from vancelle.extensions import db
from vancelle.lib.pagination import Pagination
from vancelle.lib.pagination.flask import FlaskPaginationArgs
from vancelle.models import User
from vancelle.models.work import Work

logger = structlog.get_logger(logger_name=__name__)


@dataclasses.dataclass()
class WorkController:
    def get_or_404(self, *, user: User = flask_login.current_user, id: uuid.UUID) -> Work:
        return db.session.execute(select(Work).filter_by(user_id=user.id, id=id)).scalar_one()

    def delete(self, work: Work) -> Work:
        work.time_deleted = datetime.datetime.now()
        db.session.add(work)
        db.session.commit()
        assert work.deleted is True
        return work

    def restore(self, work: Work) -> Work:
        work.time_deleted = None
        db.session.add(work)
        db.session.commit()
        assert work.deleted is False
        return work

    def permanently_delete(self, work: Work) -> None:
        db.session.delete(work)
        db.session.commit()
        return None

    def index(self) -> Pagination:
        args = FlaskPaginationArgs()

        query = sqlalchemy.select(Work).options(joinedload(Work.remotes))
        return args.query(db.session, query)
