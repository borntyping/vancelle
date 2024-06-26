from __future__ import annotations

import dataclasses
import math
import typing

T = typing.TypeVar("T")
U = typing.TypeVar("U")


@dataclasses.dataclass()
class Pagination(typing.Generic[T]):
    items: typing.Sequence[T]
    count: int

    page: int = dataclasses.field(default=1, kw_only=True)
    per_page: int = dataclasses.field(default=10, kw_only=True)

    @classmethod
    def empty(cls) -> Pagination[T]:
        return cls(items=(), count=0)

    @classmethod
    def from_iterable(cls, iterable: typing.Iterable[T]) -> Pagination[T]:
        return cls.from_sequence(tuple(iterable))

    @classmethod
    def from_sequence(cls, sequence: typing.Sequence[T]) -> Pagination[T]:
        return cls(items=sequence, count=len(sequence), page=1, per_page=len(sequence))

    def __iter__(self) -> typing.Iterator[T]:
        return iter(self.items)

    def __post_init__(self):
        if isinstance(self.items, typing.Sequence) and len(self.items) > self.per_page:
            raise ValueError(f"Too many items for this page ({len(self.items)=}, {self.per_page=})")

    def page_count(self) -> int:
        return 0 if self.count == 0 else math.ceil(self.count / self.per_page)

    @property
    def prev_page(self) -> int | None:
        return self.page - 1 if self.page > 1 else None

    def iter_page(
        self,
        *,
        start_edge: int = 2,
        prev_edge: int = 2,
        next_edge: int = 2,
        end_edge: int = 2,
    ) -> typing.Iterable[int | None]:
        final_page = self.page_count() + 1

        prev_outer = min(start_edge + 1, final_page)
        prev_inner = max(self.page - prev_edge, prev_outer)
        center_num = max(self.page, prev_inner)  # Not always the current page.
        next_inner = min(self.page + next_edge + 1, final_page)
        next_outer = max(final_page - end_edge, next_inner)

        yield from range(1, prev_outer)
        if prev_inner - prev_outer > 0:
            yield None
        yield from range(prev_inner, center_num)
        yield from range(center_num, next_inner)
        if next_outer - next_inner > 0:
            yield None
        yield from range(next_outer, final_page)

    @property
    def next_page(self) -> int | None:
        return self.page + 1 if self.page < self.page_count() else None

    def map(self, function: typing.Callable[[T], U]) -> Pagination[U]:
        return Pagination(
            items=[function(item) for item in self.items],
            count=self.count,
            page=self.page,
            per_page=self.per_page,
        )
