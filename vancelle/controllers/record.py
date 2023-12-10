import datetime
import uuid

import flask_login
import werkzeug.exceptions
from sqlalchemy.orm import joinedload

from vancelle.extensions import db
from vancelle.models.record import Record
from vancelle.models.work import Work


class RecordController:
    def get_or_404(self, *, user_id: uuid.UUID | None = None, work_id: uuid.UUID, record_id: uuid.UUID) -> Record:
        user_id = user_id or flask_login.current_user.id
        return db.one_or_404(
            db.select(Record)
            .join(Work)
            .filter(
                Work.user_id == user_id,
                Record.work_id == work_id,
                Record.id == record_id,
            )
            .options(joinedload(Record.work))
        )

    def create(self, work_id: uuid.UUID, started_today: bool = False, stopped_today: bool = False) -> Record:
        work = db.get_or_404(Work, work_id)
        record = Record(id=uuid.uuid4(), work=work)

        if started_today:
            record.date_started = datetime.date.today()

        if stopped_today:
            record.date_stopped = datetime.date.today()

        db.session.add(record)
        db.session.commit()
        return record

    def start_today(self, work_id: uuid.UUID, record_id: uuid.UUID) -> Record:
        record = self.get_or_404(work_id=work_id, record_id=record_id, user_id=flask_login.current_user.id)
        if record.date_started:
            raise werkzeug.exceptions.BadRequest("Record already has a start date")
        record.date_started = datetime.date.today()
        db.session.commit()
        return record

    def stop_today(self, work_id: uuid.UUID, record_id: uuid.UUID) -> Record:
        record = self.get_or_404(work_id=work_id, record_id=record_id)
        if record.date_stopped:
            raise werkzeug.exceptions.BadRequest("Record already has a stop date")
        record.date_stopped = datetime.date.today()
        db.session.commit()
        return record

    def delete(self, work_id: uuid.UUID, record_id: uuid.UUID) -> Record:
        record = self.get_or_404(work_id=work_id, record_id=record_id)
        record.time_deleted = datetime.datetime.now()
        db.session.commit()
        return record

    def permanently_delete(self, work_id: uuid.UUID, record_id: uuid.UUID) -> Record:
        record = self.get_or_404(work_id=work_id, record_id=record_id)
        db.session.delete(record)
        db.session.commit()
        return record

    def restore(self, work_id: uuid.UUID, record_id: uuid.UUID) -> Record:
        record = self.get_or_404(work_id=work_id, record_id=record_id)
        record.time_deleted = None
        db.session.add(record)
        db.session.commit()
        return record
