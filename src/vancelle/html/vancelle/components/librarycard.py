import dataclasses
import datetime
import itertools
import math

import humanize

from vancelle.html.bootstrap_icons import bi_svg
from vancelle.html.vancelle.components.details import Panel
from vancelle.html.vancelle.components.optional import span_absent
from vancelle.lib.heavymetal import Heavymetal, HeavymetalComponent, HeavymetalTuple
from vancelle.lib.heavymetal.html import a, div, fragment, h5, span, table, tbody, td, th, thead, tr
from vancelle.models import Record, Work


def ceil_to_even(n: int) -> int:
    return n if n % 2 == 0 else n + 1


def exact_date(date: datetime.date | None) -> HeavymetalTuple:
    if date is None:
        return span_absent()

    if not isinstance(date, datetime.date):
        raise ValueError("Not a date")

    title = humanize.naturaldate(date)
    return span({"class": "v-has-tabular-nums", "title": title}, [str(date)])


@dataclasses.dataclass()
class LibraryCard(Panel, HeavymetalComponent):
    work: Work
    min_rows: int = 10

    def heavymetal(self) -> Heavymetal:
        midpoint = max(math.ceil(len(self.work.records) / 2), self.min_rows)
        rows = itertools.zip_longest(self.work.records[:midpoint], self.work.records[midpoint:], range(self.min_rows))

        started_yesterday = a({"href": "#"}, ["yesterday"])
        started_today = a({"href": "#"}, ["today"])
        stopped_yesterday = a({"href": "#"}, ["yesterday"])
        stopped_today = a({"href": "#"}, ["today"])

        return div(
            {"class": "v-panel v-panel-records border rounded overflow-hidden"},
            [
                div(
                    {
                        "class": "v-panel-header p-1 bg-primary d-flex justify-content-center align-items-center",
                        "style": self.header_style(),
                    },
                    [
                        h5({"class": "text-light m-0 ms-1"}, "Library card"),
                    ],
                ),
                table(
                    {"class": "table text-start fs-7"},
                    [
                        thead(
                            {},
                            [
                                tr(
                                    {"class": "text-center"},
                                    [
                                        th({"class": "table-column-divider"}, ["Started"]),
                                        th({}, ["Stopped"]),
                                        th({}, ["Notes"]),
                                        th({}, []),
                                        th({"class": "table-column-divider"}, ["Started"]),
                                        th({}, ["Stopped"]),
                                        th({}, ["Notes"]),
                                        th({}, []),
                                    ],
                                )
                            ],
                        ),
                        tbody(
                            {},
                            [
                                tr(
                                    {"class": "v-panel-records-row"},
                                    [
                                        self._record(left),
                                        self._record(right),
                                    ],
                                )
                                for left, right, _ in rows
                            ],
                        ),
                    ],
                ),
                div(
                    {"class": "text-center fs-7 p-2"},
                    [
                        "new entry: started ",
                        started_today,
                        " / ",
                        started_yesterday,
                        ", stopped ",
                        stopped_today,
                        " / ",
                        stopped_yesterday,
                        "",
                    ],
                ),
            ],
        )

    @staticmethod
    def _record(record: Record | None) -> Heavymetal:
        return fragment(
            [
                td(
                    {"class": "table-column-divider"},
                    [exact_date(record.date_started)] if record else [],
                ),
                td(
                    {},
                    [exact_date(record.date_stopped)] if record else [],
                ),
                td(
                    {"class": "text-truncate"},
                    [record.notes] if record else [],
                ),
                td(
                    {"class": ""},
                    (
                        [a({"href": record.url_for()}, [bi_svg("pencil")])]
                        if record
                        else [a({"class": "text-light", "href": "#"}, [bi_svg("pencil")])]
                    ),
                ),
            ]
        )
