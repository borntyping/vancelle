import typing

from vancelle.html.helpers import HtmlClasses, html_classes
from vancelle.html.vancelle.components.pagination import nav_pagination
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import fragment, table, tbody, td, th, thead, tr
from vancelle.lib.pagination import Pagination

T = typing.TypeVar("T")


def generate_table(
    *,
    header: typing.Sequence[Heavymetal],
    row: typing.Callable[[T], typing.Sequence[Heavymetal]],
    items: typing.Iterable[T],
    classes: HtmlClasses = ("table",),
) -> Heavymetal:
    return table(
        {"class": html_classes(classes)},
        [
            thead({}, [tr({}, [th({"class": "text-start"}, [content]) for content in header])]),
            tbody({}, [tr({}, [td({}, [content]) for content in row(item)]) for item in items]),
        ],
    )


def generate_table_from_pagination(
    *,
    header: typing.Sequence[Heavymetal],
    row: typing.Callable[[T], typing.Sequence[Heavymetal]],
    pagination: Pagination[T],
    classes: HtmlClasses = ("table",),
) -> Heavymetal:
    return fragment(
        [
            generate_table(header=header, row=row, items=pagination.items, classes=classes),
            nav_pagination(pagination=pagination),
        ]
    )
