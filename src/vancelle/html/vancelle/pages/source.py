import typing

from vancelle.controllers.sources.base import Source
from vancelle.forms.source import SourceSearchArgs
from vancelle.html.vancelle.components.header import PageHeader
from vancelle.html.vancelle.pages.base import Page
from vancelle.html.vancelle.components.source import SourceListGroup, SourceSearchForm
from vancelle.html.vancelle.pages.remote import _RemoteTable
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import a, fragment
from vancelle.lib.pagination import Pagination
from vancelle.models import Remote, Work


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
    items: Pagination[Remote],
    candidate_work: typing.Optional[Work],
) -> Heavymetal:
    if candidate_work:
        subtitle = fragment([
            "New remotes will be attached to ",
            a({"href": candidate_work.url_for()}, [candidate_work.resolve_title()]),
        ])
    else:
        subtitle = "New remotes will also create a new work"

    return Page(
        [
            PageHeader(source.name, subtitle),
            SourceSearchForm(args=args, placeholder=query),
            _RemoteTable(items, candidate_work),
        ],
        title=("External sources", source.name),
    )


def ExternalDetailPage(
    *,
    remote_source: Source,
    remote: Remote,
    candidate_work: typing.Optional[Work],
):
    return Page(
        [
            PageHeader(remote.resolve_title()),
        ],
        title=("External sources", remote_source.name, remote.title),
    )
