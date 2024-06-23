import datetime
import uuid

import flask_login
import sqlalchemy
from sqlalchemy.orm import joinedload

from vancelle.extensions import db
from vancelle.models.record import Record, RelativeDate
from vancelle.models.work import Work


class RecordController:
    def select_work(self, work_id: uuid.UUID, /) -> Work:
        stmt = sqlalchemy.select(Work).filter(Work.user_id == flask_login.current_user.id).filter(Work.id == work_id)
        return db.session.execute(stmt).scalar_one()

    def select(self, record_id: uuid.UUID, /) -> Record:
        stmt = (
            sqlalchemy.select(Record)
            .filter(Record.id == record_id)
            .join(Work)
            .filter(Work.user_id == flask_login.current_user.id)
            .options(joinedload(Record.work))
        )
        return db.session.execute(stmt).scalar_one()

    def create(self, work_id: uuid.UUID, *, started: RelativeDate | None, stopped: RelativeDate | None) -> Record:
        record = Record(id=uuid.uuid4(), work_id=work_id)
        record.set_date_started(started)
        record.set_date_stopped(stopped)

        db.session.add(record)
        db.session.commit()
        return record

    def update(self, record_id: uuid.UUID, *, started: RelativeDate | None, stopped: RelativeDate | None) -> Record:
        record = self.select(record_id)
        record.set_date_started(started)
        record.set_date_stopped(stopped)

        db.session.add(record)
        db.session.commit()
        return record

    def delete(self, record_id: uuid.UUID) -> Record:
        record = self.select(record_id)
        record.time_deleted = datetime.datetime.now()

        db.session.add(record)
        db.session.commit()
        return record

    def permanently_delete(self, record_id: uuid.UUID) -> Record:
        record = self.select(record_id)

        db.session.delete(record)
        db.session.commit()
        return record

    def restore(self, record_id: uuid.UUID) -> Record:
        record = self.select(record_id)
        record.time_deleted = None
        db.session.add(record)
        db.session.commit()
        return record
