import typing

from vancelle.controllers.sources.base import Source
from vancelle.forms.source import SourceSearchArgs
from vancelle.html.vancelle.components.layout import PageHeader
from vancelle.html.vancelle.components.entry import EntryPageHeader
from vancelle.html.vancelle.pages.base import Page
from vancelle.html.vancelle.components.source import RemoteEntryDetailsPanel, SourceListGroup, SourceSearchForm, _EntryTable
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import a, fragment
from vancelle.lib.pagination import Pagination
from vancelle.models import Entry, Work


def ExternalIndexPage() -> Heavymetal:
    return Page(
        [
            PageHeader("External sources", "Provide detail for works by importing data from external sources"),
            SourceListGroup(work=None),
        ],
        title=("External sources",),
    )


def ExternalSearchPage(
    *,
    query: str,
    source: Source,
    args: SourceSearchArgs,
    items: Pagination[Entry],
    work: typing.Optional[Work],
) -> Heavymetal:
    if work:
        subtitle = fragment(["New entries will be linked to ", a({"href": work.url_for()}, [work.resolve_title()])])
    else:
        subtitle = fragment(["New entries will also create a new work"])

    return Page(
        [
            PageHeader(source.info.noun_full_plural, subtitle),
            SourceSearchForm(args=args, placeholder=query),
            _EntryTable(items, work),
        ],
        title=("External sources", source.info.noun_full_plural),
    )


def SourceDetailPage(*, source: Source, entry: Entry, work: typing.Optional[Work]):
    return Page(
        [
            EntryPageHeader(entry),
            RemoteEntryDetailsPanel(entry),
        ],
        title=("External sources", source.info.noun_full, entry.title),
    )
