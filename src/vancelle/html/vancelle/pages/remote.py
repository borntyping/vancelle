import logging
import typing

import flask

from vancelle.forms.remote import RemoteIndexArgs
from vancelle.html.bootstrap.layout.grid import col, row
from vancelle.html.vancelle.components.details import details_description
from vancelle.html.vancelle.components.header import PageHeader
from vancelle.html.vancelle.components.index import IndexFormControls
from vancelle.html.vancelle.components.optional import maybe_str, quote, quote_str
from vancelle.html.vancelle.components.panel import RemoteDetailsPanel
from vancelle.html.vancelle.components.table import generate_table_from_pagination
from vancelle.html.vancelle.pages.base import page
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import (
    a,
    button,
    form,
    td,
    th,
)
from vancelle.lib.pagination import Pagination
from vancelle.models import Remote, Work

logger = logging.getLogger(__name__)


def _create_work_button(remote: Remote) -> Heavymetal:
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


def _view_work_button(remote: Remote) -> Heavymetal:
    assert remote.work
    return a({"class": "btn btn-sm btn-secondary", "href": remote.work.url_for()}, ["View work"])


def _link_work_button(remote: Remote, candidate_work: Work) -> Heavymetal:
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


def _RemoteIndexForm(remote_index_args: RemoteIndexArgs) -> Heavymetal:
    return form(
        {"class": "v-block", "method": "get"},
        [
            row(
                {"class": "mb-3"},
                [
                    col({}, [remote_index_args.type()]),
                    col({}, [remote_index_args.deleted()]),
                ],
            ),
            row(
                {},
                [
                    col({}, [IndexFormControls(search=remote_index_args.search)]),
                ],
            ),
        ],
    )


def _RemoteTable(items: Pagination[Remote], candidate_work: typing.Optional[Work]) -> Heavymetal:
    return generate_table_from_pagination(
        attrs={},
        table_classes="table table-hover align-middle",
        cols=[
            {"style": "width: 15%;"},
            {"style": "width: 35%;"},
            {"style": "width: 35%;"},
            {"style": "width: 15%;"},
        ],
        head=[
            th({}, ["Type"]),
            th({}, ["Remote"]),
            th({}, ["Work"]),
            th({}, []),
        ],
        body=lambda remote: [
            td({}, [a({"class": "text-nowrap", "href": remote.url_for_type()}, [remote.info.noun_full])]),
            td({}, [details_description(remote.into_details(), remote.url_for(candidate_work=candidate_work))]),
            td({}, [details_description(remote.work.resolve_details(), remote.work.url_for()) if remote.work else ...]),
            td(
                {"class": "text-end"},
                [
                    _view_work_button(remote)
                    if remote.work
                    else _link_work_button(remote, candidate_work)
                    if candidate_work
                    else _create_work_button(remote)
                ],
            ),
        ],
        pagination=items,
    )


def RemoteIndexPage(
    items: Pagination[Remote],
    remote_index_args: RemoteIndexArgs,
    remote_type: typing.Type[Remote] | None,
) -> Heavymetal:
    return page(
        [
            PageHeader("Remotes", f"Work details from {remote_type.info.source if remote_type else 'external sources'}"),
            _RemoteIndexForm(remote_index_args),
            _RemoteTable(items, candidate_work=None),
        ],
        fluid=False,
        title=["Remotes"],
    )


def RemoteSearchPage(
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

    return page(
        [
            PageHeader(f"Search {remote_type.info.source}", subtitle),
            _RemoteTable(remote_items, candidate_work),
        ],
        title=[f"Search {remote_type.info.source}"],
    )


def RemoteDetailPage(remote: Remote, /, *, candidate_work: typing.Optional[Work]) -> Heavymetal:
    details = remote.into_details()
    return page(
        [
            PageHeader(maybe_str(details.title), f"{remote.info.noun_full} {remote.id}"),
            RemoteDetailsPanel(remote, candidate_work=candidate_work),
        ],
        title=["Remote", maybe_str(details.title)],
    )
