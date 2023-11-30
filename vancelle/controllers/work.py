import dataclasses
import datetime
import typing
import uuid

import flask_login
import flask_sqlalchemy.pagination
from sqlalchemy import func, select, nulls_last, Select, desc
import structlog
from sqlalchemy.orm import aliased

from vancelle.extensions import db
from vancelle.models import Base, User
from vancelle.models.remote import Remote, RemoteInfo
from vancelle.models.record import Record
from vancelle.models.work import Work
from vancelle.shelf import Shelf

logger = structlog.get_logger(logger_name=__name__)


@dataclasses.dataclass()
class WorkController:
    def select(
        self,
        *,
        user: User = flask_login.current_user,
        work_type: str,
        remote_type: str,
    ) -> Select[tuple[Work]]:
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

    def table(self, statement: Select[tuple[Work]]) -> flask_sqlalchemy.pagination.Pagination:
        return db.paginate(statement)

    def shelves(self, statement: Select[tuple[Work]]) -> typing.Mapping[Shelf, list[Work]]:
        works: typing.Iterable[Work] = db.session.execute(statement).unique().scalars().all()
        groups: dict[Shelf, list[Work]] = {shelf: [] for shelf in Shelf}
        for work in works:
            details = work.resolve_details()
            if details.shelf is None:
                raise ValueError("Work details do not include shelf")
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

    def count_works_by_type(self) -> list[tuple[str, typing.Type[Work], int]]:
        return self._count_by_type(Work)

    def count_remotes_by_type(self) -> list[tuple[str, typing.Type[Remote], int]]:
        return self._count_by_type(Remote)

    def _count_by_type(self, cls: typing.Type[Work | Remote]) -> list[tuple[str, typing.Type[Work | Remote], int]]:
        subclasses = {cls.identity(): cls for cls in cls.iter_subclasses()}
        count = func.count().label("count")
        stmt = select(cls.type, count).select_from(cls).order_by(count.desc()).group_by(cls.type)
        return [(t, subclasses[t], c) for t, c in db.session.execute(stmt)]
