from __future__ import annotations

import dataclasses
import typing

import flask
import sqlalchemy
import sqlalchemy.orm
import structlog

from .pagination import Pagination

logger = structlog.get_logger(logger_name=__name__)

T = typing.TypeVar("T")


@dataclasses.dataclass()
class FlaskPaginationArgs:
    page: int
    per_page: int
    max_per_page: int

    def __init__(self, page: int | None = None, per_page: int | None = None, max_per_page: int = 100) -> None:
        page = page if page is not None else flask.request.args.get("page", 1, int)
        per_page = per_page if per_page is not None else flask.request.args.get("per_page", 10, int)

        self.page = page
        self.per_page = min(per_page, max_per_page)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page

    def query(
        self,
        session: sqlalchemy.orm.Session,
        query_statement: sqlalchemy.Select[tuple[T]],
        count_statement: sqlalchemy.Select[tuple[int]] | None = None,
    ) -> Pagination[T]:
        items_query = query_statement.limit(self.per_page).offset(self.offset)
        items = list(session.execute(items_query).scalars())

        if count_statement:
            count = session.execute(count_statement).scalar_one()
        else:
            count_subquery = query_statement.order_by(None).limit(None).options(sqlalchemy.orm.noload("*")).subquery()
            count_query = sqlalchemy.select(sqlalchemy.func.count()).select_from(count_subquery)
            count = session.execute(count_query).scalar_one()

        return Pagination(items=items, count=count, page=self.page, per_page=self.per_page)
