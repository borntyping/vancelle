import logging
import typing

from vancelle.html.bootstrap.components.tabs import Tab, Tabs
from vancelle.html.vancelle.components.details import details_date_and_author, details_external_url, details_tags, details_title
from vancelle.html.vancelle.components.header import page_header
from vancelle.html.vancelle.components.pagination import nav_pagination
from vancelle.html.vancelle.components.table import generate_table_from_pagination
from vancelle.html.vancelle.pages.base import page
from vancelle.lib.heavymetal import Heavymetal, HeavymetalContent
from vancelle.lib.heavymetal.html import (
    a,
    code,
    div,
    figure,
    fragment,
    h3,
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
from vancelle.lib.pagination import Pagination
from vancelle.models import Remote, Work
from vancelle.models.details import Details
from vancelle.models.properties import Property

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
        title=["Remotes"],
    )


def details_panel(
    *,
    details: Details,
    properties: typing.Iterable[Property],
    data: str,
    controls,
    colour,
) -> Heavymetal:
    description = [p({}, (line,)) for line in details.description.splitlines()] if details.description else []

    tabs = Tabs(
        id="remote",
        tabs=[
            Tab("description", "Description", description),
            Tab("details", "Details", [p({}, ["...Details..."])]),
            Tab("properties", "Properties", [p({}, ["...Properties..."])]),
            Tab("data", "Data", [p({}, ["...Data..."])]),
        ],
        pane_classes="p-3 border border-top-0",
        align_tabs="center",
    )

    background = f"background-image: url('{details.background}');" if details.background else ""

    return div(
        {"class": "card"},
        [
            div({"class": "card-header", "style": background}, []),
            div(
                {"class": "card-body"},
                [
                    figure(
                        {"class": f"v-cover has-background-{colour}"},
                        [
                            (
                                img(
                                    {
                                        "class": "fs-7",
                                        "src": details.cover,
                                        "alt": f"Cover for {details.title}.",
                                        "loading": "lazy",
                                    }
                                )
                                if details.cover
                                else nothing()
                            )
                        ],
                    ),
                    h3({"class": "card-title mb-1"}, [details.title]),
                    details_date_and_author(details),
                    details_tags(details),
                    details_external_url(details),
                    div({"class": "mt-3"}, [tabs]),
                ],
            ),
        ],
    )


def remote_detail_page(remote: Remote, work: Work | None) -> Heavymetal:
    details = remote.into_details()
    return page(
        [
            page_header(details.title, span({}, [remote.info.source, " ", remote.info.noun, " ", remote.id])),
            details_panel(
                details=details,
                properties=remote.into_properties(),
                data=remote.data,
                controls=[],
                colour=remote.info.colour,
            ),
        ],
        title=["Remote", details.title],
    )
