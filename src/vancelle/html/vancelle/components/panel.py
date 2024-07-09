import dataclasses
import datetime
import itertools
import math
import textwrap
import typing

import flask
import humanize

from vancelle.html.bootstrap.components.tabs import Tab, Tabs
from vancelle.html.bootstrap_icons import bi_font, bi_svg
from vancelle.lib.html import HtmlClasses, html_classes
from vancelle.html.vancelle.components.details import DetailsDescription, DetailsJSON
from vancelle.html.vancelle.components.optional import maybe_str, span_absent
from vancelle.html.vancelle.components.properties import PropertiesTable
from vancelle.lib.heavymetal import Heavymetal, HeavymetalComponent
from vancelle.lib.heavymetal.html import (
    a,
    button,
    div,
    figure,
    form,
    fragment,
    h3,
    h5,
    img,
    nothing,
    p,
    span,
    table,
    tbody,
    td,
    th,
    thead,
    tr,
)
from vancelle.models import Record, Work
from vancelle.models.details import Details
from vancelle.models.properties import Properties


@dataclasses.dataclass(kw_only=True)
class PanelControl(HeavymetalComponent):
    icon: str
    href: str
    name: str
    title: str

    post: bool = False
    disabled: bool = False
    button_classes: HtmlClasses = dataclasses.field(default=None)

    def _btn_attrs(self):
        return

    def heavymetal(self) -> Heavymetal:
        btn = {
            "class": html_classes("btn btn-sm btn-light", {"disabled": self.disabled}, self.button_classes),
            "disabled": self.disabled,
            "title": self.title,
        }
        icon = bi_font(self.icon)

        if not self.post:
            return a({**btn, "href": self.href}, [icon])

        return form(
            {"action": self.href, "method": "post"},
            [button({**btn, "type": "submit", "hx-post": self.href}, [icon])],
        )


class Panel(HeavymetalComponent):
    def background(self) -> str | None:
        raise NotImplementedError

    def header_style(self) -> str | None:
        return f"background-image: url('{url}');" if (url := self.background()) else None


@dataclasses.dataclass()
class WorkRecordsPanel(Panel, HeavymetalComponent):
    work: Work
    min_rows: int = 10

    def background(self) -> str | None:
        return self.work.url_for_background()

    def heavymetal(self) -> Heavymetal:
        midpoint = max(math.ceil(len(self.work.records) / 2), self.min_rows)
        rows = itertools.zip_longest(self.work.records[:midpoint], self.work.records[midpoint:], range(self.min_rows))

        started_yesterday = flask.url_for("record.create", work_id=self.work.id, started="yesterday")
        started_today = flask.url_for("record.create", work_id=self.work.id, started="today")
        stopped_yesterday = flask.url_for("record.create", work_id=self.work.id, stopped="yesterday")
        stopped_today = flask.url_for("record.create", work_id=self.work.id, stopped="today")
        blank = flask.url_for("record.create", work_id=self.work.id)

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
                                        th({"class": "text-center table-column-divider"}, ["Started"]),
                                        th({"class": "text-center"}, ["Stopped"]),
                                        th({"class": "text-center"}, ["Notes"]),
                                        th({"class": "text-center"}, []),
                                        th({"class": "text-center table-column-divider"}, ["Started"]),
                                        th({"class": "text-center"}, ["Stopped"]),
                                        th({"class": "text-center"}, ["Notes"]),
                                        th({"class": "text-center"}, []),
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
                        a({"href": blank}, ["new entry"]),
                        ": started ",
                        a({"href": started_today}, ["today"]),
                        " / ",
                        a({"href": started_yesterday}, ["yesterday"]),
                        ", stopped ",
                        a({"href": stopped_today}, ["today"]),
                        " / ",
                        a({"href": stopped_yesterday}, ["yesterday"]),
                    ],
                ),
            ],
        )

    def _record(self, record: Record | None) -> Heavymetal:
        return fragment([
            td(
                {"class": "text-center table-column-divider"},
                [self.exact_date(record.date_started)] if record else [],
            ),
            td(
                {"class": "text-center"},
                [self.exact_date(record.date_stopped)] if record else [],
            ),
            td(
                {"class": "text-start text-truncate"},
                [record.notes] if record and record.notes else [],
            ),
            td(
                {"class": ""},
                (
                    [a({"href": record.url_for()}, [bi_svg("pencil")])]
                    if record
                    else [
                        a(
                            {"class": "text-body-tertiary", "href": flask.url_for("record.create", work_id=self.work.id)},
                            [bi_svg("pencil")],
                        )
                    ]
                ),
            ),
        ])

    @staticmethod
    def exact_date(date: datetime.date | None) -> Heavymetal:
        if date is None:
            return span_absent()

        if not isinstance(date, datetime.date):
            raise ValueError("Not a date")

        title = humanize.naturaldate(date)
        return span({"class": "v-has-tabular-nums", "title": title}, [str(date)])


class DetailsPanel(Panel, HeavymetalComponent):
    def id(self) -> str: ...

    def details(self) -> Details: ...

    def properties(self) -> Properties: ...

    def type_properties(self) -> Properties: ...

    def data(self) -> str | None: ...

    def cover(self) -> str | None: ...

    def background(self) -> str | None: ...

    def controls(self) -> typing.Iterable[PanelControl]: ...

    def description(self) -> Heavymetal: ...

    def tabs(self) -> typing.Iterable[Tab]:
        return ()

    def heavymetal(self) -> Heavymetal:
        details = self.details()
        tabs = Tabs(
            id=self.id(),
            align_tabs="right",
            tabs=[
                *self.tabs(),
                Tab("description", "Description", [DetailsDescription(details.description)]),
                Tab("details", "Details", [PropertiesTable(details.into_properties())]),
                Tab("properties", "Properties", [PropertiesTable(self.properties())]),
                Tab("type", "Type", [PropertiesTable(self.type_properties())]),
                Tab("data", "Data", [DetailsJSON(self.data())]),
            ],
        )

        cover = self.cover()

        return div(
            {"class": "v-panel v-panel-details border rounded overflow-hidden"},
            [
                div(
                    {
                        "class": "v-panel-header p-1 bg-primary d-flex gap-1",
                        "style": self.header_style(),
                    },
                    list(self.controls()),
                ),
                div(
                    {"class": "v-panel-cover"},
                    [
                        figure(
                            {"class": "m-0 rounded-3 bg-primary-subtle"},
                            [
                                (
                                    img({
                                        "class": "rounded-3 fs-7",
                                        "src": cover,
                                        "alt": f"Cover for {details.title}.",
                                        "loading": "lazy",
                                    })
                                    if cover
                                    else div({"class": "rounded-3 v-panel-cover-missing"}, [])
                                )
                            ],
                        )
                    ],
                ),
                div(
                    {"class": "v-panel-body"},
                    [
                        div({"class": "mb-3"}, [h3({"class": "card-title mb-1"}, [maybe_str(details.title)]), self.author()]),
                        div({"class": "text-body-secondary"}, [self.description]),
                    ],
                ),
                div({"class": "v-panel-tabs-nav"}, [tabs.navigation()]),
                div({"class": "v-panel-tabs-content"}, [tabs.content()]),
            ],
        )

    def title(self, *, href: str | None = None) -> Heavymetal:
        title = maybe_str(self.details().title)
        return a({"href": href}, [title]) if href else span({}, [title])

    def author(self) -> Heavymetal:
        if not self.details().author:
            return span_absent()

        return span({"title": self.details().author}, [textwrap.shorten(self.details().author, 50)])

    # def date_and_author(self) -> Heavymetal:
    #     year = str(self.details().release_date) if self.details().release_date else ABSENT
    #     author = textwrap.shorten(self.details().author, 50) if self.details().author else ABSENT
    #     return fragment([
    #         span({"title": maybe_str(self.details().release_date)}, [year]),
    #         ", ",
    #         span({"title": maybe_str(self.details().author)}, [author]),
    #     ])


@dataclasses.dataclass()
class WorkNotes(HeavymetalComponent):
    work: Work

    def __bool__(self) -> bool:
        return bool(self.work.notes)

    def heavymetal(self) -> Heavymetal:
        return div({"class": "text-body-secondary p-3"}, [p({}, [self.work.notes])])


@dataclasses.dataclass()
class WorkDetailsPanel(DetailsPanel):
    work: Work

    def cover(self) -> str | None:
        return self.work.resolve_details().cover

    def background(self) -> str | None:
        return self.work.resolve_details().background

    def id(self) -> str:
        return f"work-{self.work.id}"

    def details(self) -> Details:
        return self.work.resolve_details()

    def properties(self) -> Properties:
        return list(self.work.into_properties())

    def type_properties(self) -> Properties:
        return list(self.work.info.into_properties())

    def tabs(self) -> typing.Iterable[Tab]:
        yield Tab("notes", "Notes", [WorkNotes(self.work)])

    def controls(self) -> typing.Sequence[PanelControl]:
        yield PanelControl(
            href=self.work.url_for(),
            icon="database",
            name="Permalink",
            title="Permalink.",
        )
        yield PanelControl(
            href=flask.url_for("work.update", work_id=self.work.id),
            name="Edit",
            icon="pencil",
            title="Edit this work",
            disabled=self.work.deleted,
        )
        if self.work.deleted:
            yield PanelControl(
                post=True,
                href=flask.url_for("work.restore", work_id=self.work.id),
                name="Restore",
                icon="trash",
                title="Restore this work.",
                button_classes="text-success",
            )
            yield PanelControl(
                post=True,
                href=flask.url_for("work.permanently_delete", work_id=self.work.id),
                name="Permanently delete",
                icon="trash",
                title=(
                    "Permanently delete this work and any attached records and entries. "
                    "It will not be possible to recover this work."
                ),
                button_classes="text-danger",
            )
        else:
            yield PanelControl(
                post=True,
                href=flask.url_for("work.delete", work_id=self.work.id),
                name="Delete",
                icon="trash",
                title=(
                    "Delete this work and any attached records and entries. "
                    "Confirmation will be required before any data is permanently deleted."
                ),
            )

    def description(self) -> Heavymetal:
        details = self.work.resolve_details()

        if not details.release_date:
            return nothing()
        elif details.release_date >= datetime.date.today():
            return span({"class": "text-danger"}, [f"Expected to release on {details.release_date}."])
        else:
            return span({}, [f"Released {details.release_date}."])
