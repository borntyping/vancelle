import dataclasses
import datetime
import functools
import typing
import uuid

import flask_login
import sqlalchemy
import structlog
from sqlalchemy.orm import joinedload
from sqlalchemy import ColumnElement, Select, True_, desc, func, nulls_last, or_, select
from sqlalchemy.sql.functions import coalesce
from werkzeug.exceptions import BadRequest

from vancelle.exceptions import ApplicationError
from vancelle.extensions import db
from vancelle.lib.pagination import Pagination
from vancelle.lib.pagination.flask import FlaskPaginationArgs
from vancelle.models import User
from vancelle.models.record import Record
from vancelle.models.remote import ImportedWork, Remote
from vancelle.models.work import Work
from vancelle.shelf import Case, Shelf

logger = structlog.get_logger(logger_name=__name__)


@dataclasses.dataclass(frozen=True)
class WorkQuery:
    """Build SELECT queries for works."""

    user: User
    work_type: str
    work_shelf: Shelf | None
    work_case: Case | None
    work_deleted: str
    remote_type: str
    remote_data: str
    search: str

    @property
    def log(self) -> structlog.BoundLogger:
        return logger.bind(
            user=self.user.username,
            work_type=repr(self.work_type),
            work_shelf=repr(self.work_shelf),
            remote_type=repr(self.remote_type),
            remote_data=repr(self.remote_data),
            query=repr(self.search),
        )

    @functools.cached_property
    def _select_statement(self) -> Select[tuple[Work]]:
        statement = (
            select(Work)
            .select_from(Work)
            .filter(Work.user_id == self.user.id)
            .join(Record, isouter=True)
            .join(Remote, isouter=True)
            .order_by(
                nulls_last(desc(coalesce(Record.date_started, Record.date_stopped))),
                nulls_last(desc(coalesce(Work.release_date, Remote.release_date))),
                desc(Work.time_created),
            )
        )

        statement = statement.filter(self._filter_work_deleted(self.work_deleted))

        if self.work_type:
            statement = statement.filter(Work.type == self.work_type)
        if self.work_shelf:
            statement = statement.filter(Work.shelf == self.work_shelf)
        if self.work_case:
            statement = statement.filter(Work.shelf.in_(self.work_case.shelves))
        if self.remote_type:
            statement = statement.filter(Remote.type == self.remote_type)
        if self.search:
            statement = statement.filter(self._filter_query(self.search))
        if self.remote_data:
            statement = statement.filter(self._filter_remote_data(self.remote_data))

        # sub = select.options(sa_orm.lazyload("*")).order_by(None).subquery()
        # session = self._query_args["session"]

        self.log.info("Constructed query", statement=str(statement))
        return statement

    @functools.cached_property
    def _count_statement(self) -> Select[tuple[int]]:
        return self._select_statement.order_by(None).with_only_columns(func.count(Work.id.distinct()))

    def count(self) -> int:
        return db.session.execute(self._count_statement).scalar()

    def all(self) -> typing.Sequence[Work]:
        return db.session.execute(self._select_statement).unique().scalars().all()

    def shelves(self) -> typing.Tuple[typing.Mapping[Shelf, list[Work]], int]:
        """
        All shelves in the selection (in 'work_case.shelves' or equal to 'work_shelf') will appear in the result even if empty.
        Other shelves will only be present in the result if the query somehow returned them.
        """
        works = self.all()
        groups: dict[Shelf, list[Work]] = {shelf: [] for shelf in self._iter_shelves()}
        for work in works:
            groups[work.shelf].append(work)
        return groups, len(works)

    def _iter_shelves(self) -> typing.Tuple[Shelf, ...]:
        if self.work_shelf and self.work_case and self.work_shelf not in self.work_case.shelves:
            raise ApplicationError(f"The '{self.work_shelf.title}' shelf is not in the '{self.work_case.title}' group.")

        if self.work_shelf:
            return (self.work_shelf,)

        if self.work_case is not None:
            return self.work_case.shelves

        return tuple(Shelf)

    def paginate(self) -> Pagination:
        """
        Flask-SQLAlchemy doesn't calculate the right total, since the query returns
        non-unique works due to the joins to the record and remote tables.
        """
        pagination_args = FlaskPaginationArgs()
        return pagination_args.query(
            db.session,
            self._select_statement,
            self._count_statement,
        )

    @staticmethod
    def _filter_query(query: str) -> ColumnElement[bool]:
        other = f"%{query}%"
        return or_(
            Work.title.ilike(other),
            Work.author.ilike(other),
            Work.series.ilike(other),
            Work.description.ilike(other),
            Remote.title.ilike(other),
            Remote.author.ilike(other),
            Remote.series.ilike(other),
            Remote.description.ilike(other),
        )

    @staticmethod
    def _filter_work_deleted(value: str) -> ColumnElement[bool]:
        match value:
            case "yes":
                return Work.time_deleted.is_not(None)
            case "no":
                return Work.time_deleted.is_(None)
            case "all":
                return True_()

        raise BadRequest("Invalid work deleted filter")

    @staticmethod
    def _filter_remote_data(remote_data: str) -> ColumnElement[bool]:
        imported = ImportedWork.__mapper__.polymorphic_identity
        match remote_data:
            case "yes":
                return Work.remotes.any(Remote.type != imported)
            case "imported":
                return ~Work.remotes.any(Remote.type != imported)
            case "no":
                return ~Work.remotes.any()

        raise BadRequest("Invalid remote data filter")


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
