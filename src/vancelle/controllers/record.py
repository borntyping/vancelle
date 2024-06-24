import datetime
import uuid

import flask_login
import sqlalchemy
import sqlalchemy.orm
import werkzeug.exceptions

from vancelle.extensions import db
from vancelle.models import User
from vancelle.models.record import Record, RelativeDate
from vancelle.models.work import Work


class RecordController:
    def get(self, record_id: uuid.UUID, /, *, user: User = flask_login.current_user) -> Record:
        stmt = (
            sqlalchemy.select(Record)
            .filter(Record.id == record_id)
            .join(Work)
            .filter(Work.user_id == user.id)
            .options(sqlalchemy.orm.joinedload(Record.work))
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def get_or_404(self, record_id: uuid.UUID, /, *, user: User = flask_login.current_user) -> Record:
        if record := self.get(record_id, user=user):
            return record

        raise werkzeug.exceptions.NotFound(f"Record {record_id!r} not found")

    def create(self, work_id: uuid.UUID, *, started: RelativeDate | None, stopped: RelativeDate | None) -> Record:
        record = Record(id=uuid.uuid4(), work_id=work_id)
        record.set_date_started(started)
        record.set_date_stopped(stopped)

        db.session.add(record)
        db.session.commit()
        return record

    def update(self, record_id: uuid.UUID, *, started: RelativeDate | None, stopped: RelativeDate | None) -> Record:
        record = self.get_or_404(record_id)
        record.set_date_started(started)
        record.set_date_stopped(stopped)

        db.session.add(record)
        db.session.commit()
        return record

    def delete(self, record_id: uuid.UUID) -> Record:
        record = self.get_or_404(record_id)
        record.time_deleted = datetime.datetime.now()

        db.session.add(record)
        db.session.commit()
        return record

    def permanently_delete(self, record_id: uuid.UUID) -> Record:
        record = self.get_or_404(record_id)

        db.session.delete(record)
        db.session.commit()
        return record

    def restore(self, record_id: uuid.UUID) -> Record:
        record = self.get(record_id)
        record.time_deleted = None
        db.session.add(record)
        db.session.commit()
        return record
