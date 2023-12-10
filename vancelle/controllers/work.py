import dataclasses
import datetime
import typing
import uuid

import flask_login
import flask_sqlalchemy.pagination
from sqlalchemy import ColumnElement, any_, asc, exists, func, or_, select, nulls_last, Select, desc
import structlog
from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import coalesce
from werkzeug.exceptions import BadRequest

from vancelle.extensions import db
from vancelle.models import Base, User
from vancelle.models.remote import ImportedWork, Remote, RemoteInfo
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
        work_shelf: str,
        remote_type: str,
        remote_data: str,
        query: str,
    ) -> Select[tuple[Work]]:
        log = logger.bind(
            user=user.username,
            work_type=repr(work_type),
            work_shelf=repr(work_shelf),
            remote_type=repr(remote_type),
            remote_data=repr(remote_data),
            query=repr(query),
        )

        statement = (
            select(Work)
            .filter_by(user_id=user.id)
            .filter_by(time_deleted=None)
            .join(Record, isouter=True)
            .join(Remote, isouter=True)
            .order_by(
                nulls_last(desc(coalesce(Record.date_started, Record.date_stopped))),
                nulls_last(desc(coalesce(Work.release_date, Remote.release_date))),
                desc(Work.time_created),
            )
        )

        if work_type:
            statement = statement.filter(Work.type == work_type)
        if work_shelf:
            statement = statement.filter(Work.shelf == work_shelf)
        if remote_type:
            statement = statement.filter(Remote.type == remote_type)
        if query:
            statement = statement.filter(self._query_filter(query))
        if remote_data:
            statement = statement.filter(self._remote_data_filter(remote_data))

        log.info("Constructed query", statement=str(statement))
        return statement

    def _query_filter(self, query: str) -> ColumnElement[bool]:
        other = f"%{query}%"
        return or_(
            Work.title.ilike(other),
            Work.author.ilike(other),
            Work.description.ilike(other),
            Remote.title.ilike(other),
            Remote.author.ilike(other),
            Remote.description.ilike(other),
        )

    def _remote_data_filter(self, remote_data: str) -> ColumnElement[bool]:
        imported = ImportedWork.__mapper__.polymorphic_identity
        match remote_data:
            case "yes":
                return Work.remotes.any(Remote.type != imported)
            case "imported":
                return ~Work.remotes.any(Remote.type != imported)
            case "no":
                return ~Work.remotes.any()

        raise BadRequest("Invalid remote data filter")

    def paginate(self, statement: Select[tuple[Work]]) -> flask_sqlalchemy.pagination.Pagination:
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
        return self._count_by_type(Work, {cls.work_type(): cls for cls in Work.iter_subclasses()})

    def count_remotes_by_type(self) -> list[tuple[str, typing.Type[Remote], int]]:
        return self._count_by_type(Remote, {cls.remote_type(): cls for cls in Remote.iter_subclasses()})

    def _count_by_type(
        self,
        cls: typing.Type[Work | Remote],
        subclasses: typing.Mapping[str, typing.Type[Work | Remote]],
    ) -> list[tuple[str, typing.Type[Work | Remote], int]]:
        count = func.count().label("count")
        stmt = select(cls.type, count).select_from(cls).order_by(count.desc()).group_by(cls.type)
        return [(t, subclasses[t], c) for t, c in db.session.execute(stmt)]
