import dataclasses
import datetime
import typing

import markupsafe

from vancelle.blueprints.work import WorkIndexForm
from vancelle.lib.heavymetal.html import a, div, figure, h3, p, span, img, fragment
from vancelle.lib.heavymetal import Heavymetal
from vancelle.html.helpers import count_plural, html_classes
from vancelle.lib.heavymetal import HeavymetalComponent
from vancelle.html.vancelle.components.header import block_section
from vancelle.html.vancelle.components.metadata import maybe_string, span_absent, maybe_span, span_date
from vancelle.html.vancelle.pages.base import page
from vancelle.models import Work
from vancelle.shelf import Shelf


def release_date(d: datetime.date | None) -> Heavymetal:
    return span({"title": maybe_string(d)}, [str(d.year) if d else span_absent()])


def duration_span(start: datetime.date | None, stop: datetime.date | None) -> Heavymetal:
    if start and stop and start == stop:
        return span_date(start)

    return fragment([span_date(start) if start else "", markupsafe.Markup("&mdash;"), span_date(stop) if stop else ""])


def work_card(work: Work) -> Heavymetal:
    details = work.resolve_details()

    title = [a({"href": work.url_for()}, [maybe_span(details.title)])]
    subtitle = [release_date(details.release_date), ", ", maybe_span(details.author)]
    duration = [duration_span(work.date_first, work.date_last)]

    if details.cover:
        cover = [img({"src": details.cover, "alt": f"Cover for {details}.", "loading": "lazy"})]
    else:
        cover = []

    return div(
        {"class": "x-board-card box p-0 m-0", "title": str(details)},
        [
            div(
                {
                    "class": "x-board-details p-3 is-flex is-flex-direction-column is-justify-content-space-between",
                    "title": str(details),
                },
                [
                    div(
                        {},
                        [
                            h3({"class": "title is-7"}, title),
                            p({"class": "subtitle is-7  mb-3"}, subtitle),
                        ],
                    ),
                    div({}, [p({"class": "is-size-7"}, duration)]),
                ],
            ),
            figure({"class": "has-background-primary-soft"}, cover),
        ],
    )


def work_board_item(shelf: Shelf, work: Work) -> Heavymetal:
    return div({"class": "x-board-item", "data-shelf": str(shelf.value)}, [work_card(work)])


def shelf_board_item(shelf: Shelf, count: int) -> Heavymetal:
    return div(
        {
            "class": html_classes(
                "x-board-item",
                "x-board-item-header",
                "is-flex",
                "is-flex-direction-column",
                "is-justify-content-center",
                "is-align-items-center",
                "has-text-centered",
            ),
            "data-shelf": str(shelf.value),
            "data-count": str(count),
        },
        [
            h3({"class": "title is-4"}, [shelf.title]),
            p({"class": "subtitle is-7"}, [shelf.description]),
            p({"class": html_classes("block", "tag", "is-size-7")}, [count_plural("item", count)]),
        ],
    )


def vertical_board(items: typing.Sequence[Heavymetal]) -> Heavymetal:
    return div({"class": "x-board x-board-vertical"}, items)


def horizontal_board(items: typing.Sequence[Heavymetal]) -> Heavymetal:
    return div({"class": "x-board x-board-horizontal"}, items)


@dataclasses.dataclass()
class BoardPage(HeavymetalComponent):
    form: WorkIndexForm
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

        return page(block_section(board))
