import logging
import typing


from vancelle.forms.entry import EntryIndexArgs
from vancelle.html.bootstrap.layout.grid import col, row
from vancelle.html.vancelle.components.details import DetailsBox
from vancelle.html.vancelle.components.layout import PageHeader
from vancelle.html.vancelle.components.index import SearchFormControls
from vancelle.html.vancelle.components.optional import maybe_str, quote_str
from vancelle.html.vancelle.components.panel import EntryDetailsPanel
from vancelle.html.vancelle.components.table import generate_table_from_pagination
from vancelle.html.vancelle.pages.base import Page
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import (
    a,
    form,
    td,
    th,
)
from vancelle.lib.pagination import Pagination
from vancelle.models import Entry, Work

logger = logging.getLogger(__name__)


def _EntryIndexForm(entry_index_args: EntryIndexArgs) -> Heavymetal:
    return form(
        {"class": "v-block", "method": "get"},
        [
            row(
                {"class": "mb-3"},
                [
                    col({}, [entry_index_args.type()]),
                    col({}, [entry_index_args.deleted()]),
                ],
            ),
            row(
                {},
                [
                    col({}, [SearchFormControls(field=entry_index_args.search)]),
                ],
            ),
        ],
    )


def _EntryTable(items: Pagination[Entry]) -> Heavymetal:
    return generate_table_from_pagination(
        table_classes="table table-hover align-middle",
        cols=[
            {"style": "width: 20%;"},
            {"style": "width: 40%;"},
            {"style": "width: 40%;"},
        ],
        head=[
            th({}, ["Entry Type"]),
            th({}, ["Entry"]),
            th({}, ["Work"]),
            th({}, []),
        ],
        body=lambda entry: [
            td({}, [a({"class": "text-nowrap", "href": entry.url_for_index()}, [entry.info.noun_full])]),
            td({}, [DetailsBox(entry.into_details(), entry.url_for())]),
            td({}, [DetailsBox(entry.work.resolve_details(), entry.work.url_for()) if entry.work else ...]),
        ],
        pagination=items,
    )


def EntryIndexPage(
    items: Pagination[Entry],
    entry_index_args: EntryIndexArgs,
    entry_type: typing.Type[Entry] | None,
) -> Heavymetal:
    return Page(
        [
            PageHeader("Entries", f"Entries from {entry_type.info.origin if entry_type else 'external sources'}"),
            _EntryIndexForm(entry_index_args),
            _EntryTable(items),
        ],
        fluid=False,
        title=["Entries"],
    )


def EntrySearchPage(
    *,
    entry_cls: typing.Type[Entry],
    entry_items: Pagination[Entry],
    candidate_work: typing.Optional[Work],
) -> Heavymetal:
    """TODO: deprecated?"""

    if candidate_work:
        details = candidate_work.resolve_details()
        subtitle = f"Link {entry_cls.info.noun_full} to {quote_str(details.title)}"
    else:
        subtitle = None

    return Page(
        [
            PageHeader(f"Search {entry_cls.info.origin}", subtitle),
            _EntryTable(entry_items, candidate_work),
        ],
        title=[f"Search {entry_cls.info.origin}"],
    )


def EntryDetailPage(entry: Entry) -> Heavymetal:
    details = entry.into_details()
    return Page(
        [
            PageHeader(maybe_str(details.title), f"{entry.info.noun_full} {entry.id}"),
            EntryDetailsPanel(entry),
        ],
        title=["Entry", maybe_str(details.title)],
    )
