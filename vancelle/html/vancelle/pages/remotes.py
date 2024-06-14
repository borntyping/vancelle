import logging
import typing

from vancelle.html.vancelle.components.details import DetailsPanel
from vancelle.html.vancelle.components.header import page_header
from vancelle.html.vancelle.components.optional import maybe_string
from vancelle.html.vancelle.components.table import generate_table_from_pagination
from vancelle.html.vancelle.pages.base import page
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import (
    a,
    code,
    div,
    span,
    td,
    tr,
)
from vancelle.lib.pagination import Pagination
from vancelle.models import Remote, Work
from vancelle.models.details import Details

logger = logging.getLogger(__name__)


def _remote_id(remote: Remote) -> Heavymetal:
    return code({"class": "v-text-wrap-anywhere"}, [remote.remote_type(), ":", remote.id])


def _remote_type(remote: Remote) -> Heavymetal:
    return a({"class": "text-nowrap", "href": remote.url_for_type()}, [remote.info.noun_full])


def _description(details: Details, href: str) -> Heavymetal:
    wrapper = DetailsPanel(details)
    return div(
        {},
        [
            div({}, [wrapper.title(href=href)]),
            div({"class": "text-body-tertiary"}, [wrapper.date_and_author()]),
        ],
    )


def remote_index_page_row(remote: Remote) -> Heavymetal:
    remote_details = remote.into_details()
    resolved_details = remote.work.resolve_details()
    return tr(
        {},
        [
            td({}, [_remote_type(remote)]),
            td({}, [_description(remote_details, remote.url_for())]),
            td({}, [_description(resolved_details, remote.work.url_for())]),
        ],
    )


def remote_index_page(remote_type: typing.Type[Remote] | None, remotes: Pagination[Remote]) -> Heavymetal:
    remotes_table = generate_table_from_pagination(
        classes="table table-hover table-sm",
        header=[
            "Source",
            "Title",
            "Work",
        ],
        row=lambda remote: [
            _remote_type(remote),
            _description(remote.into_details(), remote.url_for()),
            _description(remote.work.resolve_details(), remote.work.url_for()),
        ],
        pagination=remotes,
    )

    return page(
        [
            page_header("Remotes", f"Work details from {remote_type.info.source if remote_type else 'external sources'}"),
            remotes_table,
        ],
        fluid=False,
        title=["Remotes"],
    )


def remote_detail_page(remote: Remote, work: Work | None) -> Heavymetal:
    details = remote.into_details()
    properties = list(remote.into_properties())
    panel = DetailsPanel(
        details=details,
        properties=properties,
        data=remote.data,
        background_colour=remote.info.colour,
    )
    subtitle = span({}, [remote.info.source, " ", remote.info.noun, " ", remote.id])
    return page(
        [page_header(maybe_string(details.title), subtitle), panel],
        title=["Remote", maybe_string(details.title)],
    )
