import dataclasses
import datetime
import typing
import uuid

import flask_login
import flask_sqlalchemy.pagination
from sqlalchemy import func, select, nulls_last, Select, desc
import structlog

from vancelle.extensions import db
from vancelle.models.metadata import Source
from vancelle.models import Base, User
from vancelle.models.remote import Remote
from vancelle.models.record import Record
from vancelle.models.work import Work
from vancelle.types import Shelf

logger = structlog.get_logger(logger_name=__name__)


@dataclasses.dataclass()
class WorkController:
    def select(
        self,
        *,
        user: User = flask_login.current_user,
        work_type: str,
        remote_type: str,
    ) -> Select[(Work,)]:
        statement = (
            select(Work)
            .filter_by(user_id=user.id)
            .filter_by(time_deleted=None)
            .join(Record, isouter=True)
            .order_by(
                nulls_last(desc(Record.date_stopped)),
                nulls_last(desc(Record.date_started)),
                desc(Work.time_created),
            )
        )

        if work_type:
            statement = statement.filter(Work.type == work_type)

        if remote_type:
            statement = statement.join(Remote).filter(Remote.type == remote_type)

        return statement

    def table(self, statement: Select[Work]) -> flask_sqlalchemy.pagination.Pagination:
        return db.paginate(statement)

    def shelves(self, statement: Select[Work]) -> typing.Mapping[Shelf, list[Work]]:
        works: list[Work] = db.session.execute(statement).unique().scalars().all()
        groups = {shelf: [] for shelf in Shelf}
        for work in works:
            details = work.resolve_details()
            groups[details.shelf].append(work)
        return groups

    def get_or_404(self, *, user: User = flask_login.current_user, id: uuid.UUID) -> Work:
        return db.one_or_404(select(Work).filter_by(user_id=user.id, id=id))

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

    def count(self, table: typing.Type[Base], **kwargs: typing.Any) -> int:
        return db.session.execute(select(func.count()).select_from(table).filter_by(**kwargs)).scalar_one()

    def count_works_by_type(self) -> list[(str, int)]:
        counts = db.session.execute(select(Work.type, func.count()).select_from(Work).order_by(Work.type).group_by(Work.type))
        return counts

    def count_remotes_by_type(self) -> typing.Iterable[typing.Tuple[str, int, Source]]:
        sources = Remote.sources()
        counts = db.session.execute(
            select(Remote.type, func.count()).select_from(Remote).order_by(Remote.type).group_by(Remote.type)
        )
        return [(t, count, sources[t]) for t, count in counts]
