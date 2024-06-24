import typing

import flask

from vancelle.controllers.sources.base import Source
from vancelle.forms.source import SourceSearchArgs
from vancelle.html.vancelle.components.details import DetailsBox
from vancelle.html.vancelle.components.layout import PageHeader
from vancelle.html.vancelle.components.optional import quote
from vancelle.html.vancelle.components.table import generate_table_from_pagination
from vancelle.html.vancelle.pages.base import Page
from vancelle.html.vancelle.components.source import SourceListGroup, SourceSearchForm
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import a, button, form, fragment, td, th
from vancelle.lib.pagination import Pagination
from vancelle.models import Entry, Work


def _ImportButton(entry: Entry, candidate_work: Work) -> Heavymetal:
    if entry.work:
        return a({"class": "btn btn-sm btn-secondary", "href": entry.work.url_for()}, ["View existing work"])

    title = entry.resolve_title()
    action = flask.url_for(
        "source.import",
        entry_type=entry.type,
        entry_id=entry.id,
        candidate_work_id=candidate_work.id if candidate_work else None,
    )
    return form(
        {"method": "post", "action": action},
        [button({"class": "btn btn-sm btn-primary", "type": "submit", "title": f"Import {quote(title)}."}, ["Import"])],
    )


def _RemoteEntryTable(items: Pagination[Entry], candidate_work: typing.Optional[Work]) -> Heavymetal:
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
                            candidate_work_id=candidate_work.id if candidate_work else None,
                        ),
                    )
                ],
            ),
            td({"class": "text-end"}, [_ImportButton(entry, candidate_work)]),
        ],
        pagination=items,
    )


def ExternalIndexPage(sources: typing.Sequence[Source]) -> Heavymetal:
    return Page(
        [
            PageHeader("External sources", "Provide detail for works by importing data from external sources"),
            SourceListGroup(sources, candidate_work=None),
        ],
        title=("External sources",),
    )


def ExternalSearchPage(
    *,
    query: str,
    source: Source,
    args: SourceSearchArgs,
    items: Pagination[Entry],
    candidate_work: typing.Optional[Work],
) -> Heavymetal:
    if candidate_work:
        subtitle = fragment([
            "New entries will be linked to ",
            a({"href": candidate_work.url_for()}, [candidate_work.resolve_title()]),
        ])
    else:
        subtitle = "New entries will also create a new work"

    return Page(
        [
            PageHeader(source.info.noun_full_plural, subtitle),
            SourceSearchForm(args=args, placeholder=query),
            _RemoteEntryTable(items, candidate_work),
        ],
        title=("External sources", source.info.noun_full_plural),
    )


def SourceDetailPage(
    *,
    source: Source,
    entry: Entry,
    candidate_work: typing.Optional[Work],
):
    return Page(
        [
            PageHeader(entry.resolve_title()),
        ],
        title=("External sources", source.info.noun_full, entry.title),
    )
