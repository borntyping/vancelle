from __future__ import annotations

import sqlalchemy
import wtforms

from vancelle.lib.pagination import Pagination
from vancelle.lib.pagination.flask import T


class PaginationArgs(wtforms.Form):
    page = wtforms.IntegerField(default=1, validators=[wtforms.validators.NumberRange(min=1)])
    per_page = wtforms.IntegerField(default=10, validators=[wtforms.validators.NumberRange(min=1, max=100)])

    def query(
        self,
        session: sqlalchemy.orm.Session,
        query_statement: sqlalchemy.Select[tuple[T]],
        count_statement: sqlalchemy.Select[tuple[int]] | None = None,
    ) -> Pagination[T]:
        page = self.page.data
        per_page = self.per_page.data

        offset = (page - 1) * per_page
        items_query = query_statement.limit(per_page).offset(offset)
        items = list(session.execute(items_query).unique().scalars())

        if count_statement is not None:
            count = session.execute(count_statement).scalar_one()
        else:
            count_subquery = query_statement.order_by(None).limit(None).options(sqlalchemy.orm.noload("*")).subquery()
            count_query = sqlalchemy.select(sqlalchemy.func.count()).select_from(count_subquery)
            count = session.execute(count_query).scalar_one()

        return Pagination(items=items, count=count, page=page, per_page=per_page)
