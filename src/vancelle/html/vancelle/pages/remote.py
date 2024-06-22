import logging
import typing

import flask

from vancelle.html.vancelle.components.details import details_description
from vancelle.html.vancelle.components.header import page_header
from vancelle.html.vancelle.components.optional import maybe_str, quote, quote_str
from vancelle.html.vancelle.components.panel import RemoteDetailsPanel
from vancelle.html.vancelle.components.table import generate_table_from_pagination
from vancelle.html.vancelle.pages.base import page
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import (
    a,
    button,
    code,
    form,
    td,
    th,
    tr,
)
from vancelle.lib.pagination import Pagination
from vancelle.models import Remote, Work

logger = logging.getLogger(__name__)


def _remote_id(remote: Remote) -> Heavymetal:
    return code({"class": "v-text-wrap-anywhere"}, [remote.remote_type(), ":", remote.id])


def _remote_type(remote: Remote) -> Heavymetal:
    return a({"class": "text-nowrap", "href": remote.url_for_type()}, [remote.info.noun_full])


def remote_index_page_row(remote: Remote) -> Heavymetal:
    remote_details = remote.into_details()
    resolved_details = remote.work.resolve_details()
    return tr(
        {},
        [
            td({}, [_remote_type(remote)]),
            td({}, [details_description(remote_details, remote.url_for())]),
            td({}, [details_description(resolved_details, remote.work.url_for())]),
        ],
    )


def remote_index_page(remote_type: typing.Type[Remote] | None, remotes: Pagination[Remote]) -> Heavymetal:
    remotes_table = generate_table_from_pagination(
        classes="table table-hover table-sm align-middle",
        cols=[
            {"style": "width: 20%;"},
            {"style": "width: 40%;", "colspan": "2"},
        ],
        head=[
            th({}, ["Source"]),
            th({}, ["Title"]),
            th({}, ["Work"]),
        ],
        body=lambda remote: [
            td({}, [_remote_type(remote)]),
            td({}, [details_description(remote.into_details(), remote.url_for())]),
            td({}, [details_description(remote.work.resolve_details(), remote.work.url_for())]),
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


def remote_detail_page(remote: Remote, /, *, candidate_work: typing.Optional[Work]) -> Heavymetal:
    details = remote.into_details()
    return page(
        [
            page_header(maybe_str(details.title), f"{remote.info.noun_full} {remote.id}"),
            RemoteDetailsPanel(remote, candidate_work=candidate_work),
        ],
        title=["Remote", maybe_str(details.title)],
    )


def create_work_button(remote: Remote) -> Heavymetal:
    action = flask.url_for("remote.create_work", remote_type=remote.type, remote_id=remote.id)
    return form(
        {"method": "post", "action": action},
        [
            button(
                {
                    "class": "btn btn-sm btn-primary",
                    "type": "submit",
                    "disabled": False,
                    "title": "Create a new work linked to this remote.",
                },
                ["Create new work"],
            )
        ],
    )


def link_work_button(remote: Remote, candidate_work: Work) -> Heavymetal:
    details = candidate_work.resolve_details()
    return form(
        {
            "method": "post",
            "action": flask.url_for(
                "remote.link_work",
                work_id=candidate_work.id,
                remote_type=remote.type,
                remote_id=remote.id,
            ),
        },
        [
            button(
                {
                    "class": "btn btn-sm btn-primary",
                    "type": "submit",
                    "disabled": False,
                    "title": f"Link work to {details.title}.",
                },
                ["Link work to ", quote(details.title)],
            )
        ],
    )


def remote_search_page(
    *,
    remote_type: typing.Type[Remote],
    remote_items: Pagination[Remote],
    candidate_work: typing.Optional[Work],
) -> Heavymetal:
    if candidate_work:
        details = candidate_work.resolve_details()
        subtitle = f"Link {remote_type.info.noun_full} to {quote_str(details.title)}"
    else:
        subtitle = None

    remotes_table = generate_table_from_pagination(
        classes="table table-hover align-middle",
        head=[
            th({}, ["Title"]),
            th({}, []),
        ],
        body=lambda remote: [
            td({}, [details_description(remote.into_details(), remote.url_for(candidate_work=candidate_work))]),
            td(
                {"class": "text-end"},
                [link_work_button(remote, candidate_work) if candidate_work else create_work_button(remote)],
            ),
        ],
        pagination=remote_items,
    )

    return page(
        [
            page_header(f"Search {remote_type.info.source}", subtitle),
            remotes_table,
        ],
        title=[f"Search {remote_type.info.source}"],
    )
