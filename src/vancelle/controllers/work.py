import dataclasses
import datetime
import uuid

import flask_login
import structlog
from sqlalchemy import select
from werkzeug.exceptions import NotFound

from vancelle.extensions import db
from vancelle.models import User
from vancelle.models.work import Work

logger = structlog.get_logger(logger_name=__name__)


@dataclasses.dataclass()
class WorkController:
    def get(self, work_id: uuid.UUID, /, *, user: User = flask_login.current_user) -> Work:
        return db.session.execute(select(Work).filter_by(user_id=user.id, id=work_id)).scalar_one_or_none()

    def get_or_404(self, work_id: uuid.UUID, /, *, user: User = flask_login.current_user):
        if work := self.get(work_id, user=user):
            return work

        raise NotFound(f"Work {work_id} not found")

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
