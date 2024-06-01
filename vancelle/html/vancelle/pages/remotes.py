import logging
import typing

from vancelle.ext.flask_sqlalchemy import Pagination
from vancelle.html.vancelle.components.details import details_date_and_author, details_title
from vancelle.html.vancelle.components.header import page_header
from vancelle.html.vancelle.components.pagination import nav_pagination
from vancelle.html.vancelle.components.table import generate_table_from_pagination
from vancelle.html.vancelle.pages.base import page
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import a, code, div, table, tbody, td, th, thead, tr
from vancelle.models import Remote
from vancelle.models.details import Details

logger = logging.getLogger(__name__)


def _remote_id(remote: Remote) -> Heavymetal:
    return code({"class": "v-text-wrap-anywhere"}, [remote.remote_type(), ":", remote.id])


def _remote_type(remote: Remote) -> Heavymetal:
    return a({"class": "text-nowrap", "href": remote.url_for_type()}, [remote.info.noun_full])


def _description(details: Details, href: str) -> Heavymetal:
    return div(
        {},
        [
            div({}, [details_title(details, href=href)]),
            div({"class": "text-body-tertiary"}, [details_date_and_author(details)]),
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
    )
