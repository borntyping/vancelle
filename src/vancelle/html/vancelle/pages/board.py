import dataclasses
import datetime
import typing

import markupsafe

from vancelle.extensions import html
from vancelle.forms.work import WorkIndexArgs
from vancelle.lib.heavymetal.html import a, div, figure, h3, p, section, span, img, fragment
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.html import html_classes
from vancelle.lib.heavymetal import HeavymetalComponent
from vancelle.html.vancelle.components.metadata import span_date
from vancelle.html.vancelle.components.optional import maybe_span, maybe_str, span_absent
from vancelle.html.vancelle.pages.base import page
from vancelle.models import Work
from vancelle.shelf import Shelf


def release_date(d: datetime.date | None) -> Heavymetal:
    return span({"title": maybe_str(d)}, [str(d.year) if d else span_absent()])


def duration_span(start: datetime.date | None, stop: datetime.date | None) -> Heavymetal:
    if start and stop and start == stop:
        return span_date(start)

    return fragment([span_date(start) if start else "", markupsafe.Markup(" &mdash; "), span_date(stop) if stop else ""])


def work_board_item(shelf: Shelf, work: Work) -> Heavymetal:
    details = work.resolve_details()

    title = a(
        {
            "class": html_classes(["stretched-link-x", "text-decoration-none", "text-primary-emphasis"]),
            "href": work.url_for(),
        },
        [
            maybe_span(details.title),
        ],
    )
    subtitle = fragment([release_date(details.release_date), ", ", maybe_span(details.author)])
    duration = duration_span(work.date_first, work.date_last)

    if details.cover:
        cover = [img({"src": details.cover, "alt": f"Cover for {details}.", "loading": "lazy"})]
    else:
        cover = []

    return div(
        {
            "class": html_classes(
                ["x-board-item", "x-board-card"],
                ["overflow-hidden", "position-relative"],
                ["border", "rounded", "shadow-sm", "bg-body-tertiary"],
            ),
            "data-shelf": str(shelf.value),
            "title": str(details),
        },
        [
            div(
                {
                    "class": html_classes(
                        ["x-board-detail"],
                        ["d-flex", "flex-column", "justify-content-between"],
                        ["p-2"],
                    ),
                    "title": str(details),
                },
                [
                    div(
                        {},
                        [
                            h3({"class": "x-board-line fs-7 fw-bold"}, [title]),
                            span({"class": "x-board-line fs-7"}, [subtitle]),
                        ],
                    ),
                    div(
                        {},
                        [
                            span({"class": "x-board-line fs-7"}, [duration]),
                        ],
                    ),
                ],
            ),
            figure({"class": "m-0 p-0 bg-info-subtle"}, cover),
        ],
    )


def shelf_board_item(shelf: Shelf, count: int) -> Heavymetal:
    return div(
        {
            "class": html_classes(
                ["x-board-item", "x-board-item-header"],
                ["d-flex", "flex-column", "align-items-center", "justify-content-center"],
                ["overflow-hidden", "fs-6", "has-text-centered"],
            ),
            "data-shelf": str(shelf.value),
            "data-count": str(count),
        },
        [
            h3({"class": "display-7"}, [shelf.title]),
            p({"class": "fs-7"}, [shelf.description]),
            span({"class": "badge bg-primary rounded-pill"}, [html.count_plural("item", count)]),
        ],
    )


def vertical_board(items: typing.Sequence[Heavymetal]) -> Heavymetal:
    return div({"class": "x-board x-board-vertical"}, items)


def horizontal_board(items: typing.Sequence[Heavymetal]) -> Heavymetal:
    return div({"class": "x-board x-board-horizontal"}, items)


@dataclasses.dataclass()
class BoardPage(HeavymetalComponent):
    form: WorkIndexArgs
    layout: typing.Literal["vertical", "horizontal"]
    shelves: typing.Mapping[Shelf, list[Work]]
    total: int

    def heavymetal(self) -> Heavymetal:
        items = []
        for shelf, works in self.shelves.items():
            items.append(shelf_board_item(shelf, len(works)))
            for work in works:
                items.append(work_board_item(shelf, work))

        if self.layout == "vertical":
            board = vertical_board(items)
        elif self.layout == "horizontal":
            board = horizontal_board(items)
        else:
            raise ValueError

        return page([section({}, [board])], title=["Board"])
