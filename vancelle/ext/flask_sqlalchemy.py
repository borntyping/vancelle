import typing

import flask_sqlalchemy.pagination
import sqlalchemy
from sqlalchemy.orm import Session

T = typing.TypeVar("T")
U = typing.TypeVar("U")


class Pagination(flask_sqlalchemy.pagination.Pagination, typing.Generic[T]):
    def __iter__(self) -> typing.Iterator[T]:
        return super().__iter__()

    def _query_items(self) -> typing.Sequence[T]:
        return super()._query_items()


class EmptyPagination(Pagination[T]):
    def _query_items(self) -> list:
        return []

    def _query_count(self) -> int:
        return 0


class ItemsPagination(Pagination[T]):
    def __init__(
        self,
        *,
        page: int | None = None,
        per_page: int | None = None,
        max_per_page: int | None = 100,
        error_out: bool = True,
        count: bool = True,
        items: typing.Sequence[T],
        total: int | None = None,
    ) -> None:
        """
        >>> ItemsPagination(items=[1, 2, 3]).items
        [1, 2, 3]
        >>> ItemsPagination(items=[1, 2, 3]).total
        3
        """
        self.__items = items
        self.__total = total or len(items)
        super().__init__(page=page, per_page=per_page, max_per_page=max_per_page, error_out=error_out, count=count)

    def _query_items(self) -> typing.Sequence[T]:
        return self.__items

    def _query_count(self) -> int:
        return self.__total


class StaticPagination(Pagination[T]):
    def __init__(self, *, items: typing.Sequence[T]) -> None:
        self.__items = items
        self.__total = len(items)
        super().__init__(page=1, per_page=max(self.__total, 1), max_per_page=max(self.__total, 1), count=True)

    def _query_items(self) -> typing.Sequence[T]:
        return self.__items

    def _query_count(self) -> int:
        return self.__total


class SelectPagination(flask_sqlalchemy.pagination.SelectPagination, typing.Generic[T]):
    def __init__(
        self,
        *,
        page: int | None = None,
        per_page: int | None = None,
        max_per_page: int | None = 100,
        error_out: bool = True,
        count: bool = True,
        select: sqlalchemy.Select[tuple[T]],
        session: Session,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(
            page=page,
            per_page=per_page,
            max_per_page=max_per_page,
            error_out=error_out,
            count=count,
            select=select,
            session=session,
            **kwargs,
        )

    def __iter__(self) -> typing.Iterator[T]:
        return super().__iter__()

    def _query_items(self) -> typing.Sequence[T]:
        return super()._query_items()


class SelectAndTransformPagination(SelectPagination[T], typing.Generic[T, U]):
    def __init__(
        self,
        *,
        page: int | None = None,
        per_page: int | None = None,
        max_per_page: int | None = 100,
        error_out: bool = True,
        count: bool = True,
        select: sqlalchemy.Select[tuple[U]],
        session: Session,
        transform: typing.Callable[[U], T],
    ) -> None:
        self.__transform = transform
        super().__init__(
            page=page,
            per_page=per_page,
            max_per_page=max_per_page,
            error_out=error_out,
            count=count,
            select=select,
            session=session,
        )

    def _query_items(self) -> list[T]:
        items = super()._query_items()
        return [self.__transform(item) for item in items]
