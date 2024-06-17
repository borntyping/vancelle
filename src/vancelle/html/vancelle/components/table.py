import typing

from vancelle.html.helpers import HtmlClasses, html_classes
from vancelle.html.vancelle.components.pagination import nav_pagination
from vancelle.lib.heavymetal import Heavymetal, HeavymetalAttrs
from vancelle.lib.heavymetal.html import col, colgroup, fragment, table, tbody, thead, tr
from vancelle.lib.pagination import Pagination

T = typing.TypeVar("T")


def generate_table(
    *,
    cols: typing.Sequence[HeavymetalAttrs] = (),
    head: typing.Sequence[Heavymetal],
    body: typing.Callable[[T], typing.Sequence[Heavymetal]],
    items: typing.Iterable[T],
    classes: HtmlClasses = "table align-middle",
) -> Heavymetal:
    return table(
        {"class": html_classes(classes)},
        [
            colgroup({}, [col(attrs) for attrs in cols]),
            thead({"data-debug": "generate_table().thead"}, [tr({}, head)]),
            tbody({"data-debug": "generate_table().tbody"}, [tr({}, body(item)) for item in items]),
        ],
    )


def generate_table_from_pagination(
    *,
    cols: typing.Sequence[HeavymetalAttrs] = (),
    head: typing.Sequence[Heavymetal],
    body: typing.Callable[[T], typing.Sequence[Heavymetal]],
    pagination: Pagination[T],
    classes: HtmlClasses = "table align-middle",
) -> Heavymetal:
    return fragment([
        generate_table(cols=cols, head=head, body=body, items=pagination.items, classes=classes),
        nav_pagination(pagination=pagination),
    ])
