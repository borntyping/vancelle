import dataclasses
import typing

import flask

from vancelle.controllers.sources.base import Source
from vancelle.forms.source import SourceSearchArgs
from vancelle.html.bootstrap.layout.grid import col, row
from vancelle.html.vancelle.components.details import DetailsBox
from vancelle.html.vancelle.components.index import SearchFormControls
from vancelle.html.vancelle.components.optional import quote_str
from vancelle.html.vancelle.components.panel import DetailsPanel, PanelControl
from vancelle.html.vancelle.components.table import generate_table_from_pagination
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import a, button, code, div, form, fragment, p, td, th
from vancelle.lib.pagination import Pagination
from vancelle.models import Entry, Work
from vancelle.models.details import Details
from vancelle.models.properties import Properties


def SourceListGroup(work: typing.Optional[Work]) -> Heavymetal:
    return div(
        {"class": "list-group"},
        [
            a(
                {"class": "list-group-item list-group-item-action", "href": source.url_for_search(work)},
                ["Search ", source.info.noun_full_plural],
            )
            for source in Source.subclasses()
        ],
    )


def SourceSearchForm(args: SourceSearchArgs, placeholder: str) -> Heavymetal:
    return form(
        {"class": "v-block", "method": "get"},
        [row({}, [col({}, [SearchFormControls(field=args.search, placeholder=placeholder)])])],
    )


def _ImportEntryButton(entry: Entry, work: Work) -> Heavymetal:
    if entry.work:
        return a({"class": "btn btn-sm btn-secondary", "href": entry.work.url_for()}, ["View existing work"])

    title = entry.resolve_title()
    action = flask.url_for("source.import", entry_type=entry.type, entry_id=entry.id, work_id=work.id if work else None)
    return form(
        {"method": "post", "action": action},
        [button({"class": "btn btn-sm btn-primary", "type": "submit", "title": f"Import {quote_str(title)}."}, ["Import"])],
    )


def _EntryTable(items: Pagination[Entry], work: typing.Optional[Work]) -> Heavymetal:
    return generate_table_from_pagination(
        table_classes="table table-hover align-middle",
        cols=[
            {"style": "width: 20%;"},
            {"style": "width: 60%;"},
            {"style": "width: 20%;"},
        ],
        head=[
            th({}, ["Entry Type"]),
            th({}, ["Entry"]),
            th({}, []),
        ],
        body=lambda entry: [
            td({}, [a({"class": "text-nowrap", "href": entry.url_for_index()}, [entry.info.noun_full])]),
            td(
                {},
                [
                    DetailsBox(
                        entry.into_details(),
                        flask.url_for(
                            "source.detail",
                            entry_type=entry.type,
                            entry_id=entry.id,
                            work_id=work.id if work else None,
                        ),
                    )
                ],
            ),
            td({"class": "text-end"}, [_ImportEntryButton(entry, work)]),
        ],
        pagination=items,
    )


@dataclasses.dataclass()
class RemoteEntryDetailsPanel(DetailsPanel):
    entry: Entry

    def id(self) -> str:
        return f"entry-{self.entry.id}"

    def cover(self) -> str | None:
        return self.entry.cover

    def background(self) -> str | None:
        return self.entry.background

    def details(self) -> Details:
        return self.entry.into_details()

    def properties(self) -> Properties:
        return list(self.entry.into_properties())

    def type_properties(self) -> Properties:
        return list(self.entry.info.into_properties())

    def data(self) -> str | None:
        return self.entry.data

    def controls(self) -> typing.Sequence[PanelControl]:
        return ()

    def description(self) -> Heavymetal:
        link = a(
            {
                "class": "link-body-emphasis",
                "href": self.entry.external_url(),
                "rel": "noopener noreferrer nofollow",
                "target": "_blank",
            },
            [f"{self.entry.info.noun_full} ", code({}, self.entry.id)],
        )
        released = [f", released {self.entry.release_date}"] if self.entry.release_date else []
        description = p({}, [link, *released, "."])

        return fragment([description])
