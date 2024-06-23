import flask

from vancelle.extensions import html
from vancelle.forms.work import WorkForm, WorkShelfForm, WorkIndexArgs
from vancelle.html.bootstrap.components.button_group import btn_group
from vancelle.html.bootstrap.forms.controls import form_control
from vancelle.html.bootstrap.layout.grid import col, row
from vancelle.html.vancelle.components.details import details_description
from vancelle.html.vancelle.components.header import page_header, section_header
from vancelle.html.vancelle.components.optional import maybe_str, maybe_year, quote_str
from vancelle.html.vancelle.components.panel import RemoteDetailsPanel, WorkDetailsPanel, WorkRecordsPanel
from vancelle.html.vancelle.components.table import generate_table_from_pagination
from vancelle.html.vancelle.components.work import return_to_work
from vancelle.html.vancelle.pages.base import page
from vancelle.lib.heavymetal import Heavymetal, HeavymetalContent
from vancelle.lib.heavymetal.html import a, button, div, form, section, td, th
from vancelle.lib.pagination import Pagination
from vancelle.models import Remote, Work
from vancelle.models.details import Details, EMPTY_DETAILS


def _search_for_work(work: Work) -> Heavymetal:
    subclasses = Remote.iter_subclasses_interactive()
    return div(
        {"class": "list-group"},
        [
            a(
                {
                    "class": "list-group-item list-group-item-action",
                    "href": flask.url_for("remote.search_source", remote_type=remote_type, work_id=work.id),
                },
                ["Search ", remote_type.info.noun_full_plural],
            )
            for remote_type in subclasses
        ],
    )


def _work_form_page(
    *,
    work_form: WorkForm,
    details: Details,
    title: str,
    subtitle: str,
    action: str,
    page_title: list[str],
    btn_groups: HeavymetalContent,
) -> Heavymetal:
    return page(
        [
            form(
                {"method": "post", "action": action},
                [
                    page_header(
                        title,
                        subtitle,
                        div(
                            {"class": "btn-toolbar gap-3"},
                            [
                                *btn_groups,
                                btn_group([
                                    button({"class": "btn btn-lg btn-primary", "type": "submit"}, ["Save"]),
                                ]),
                            ],
                        ),
                    ),
                    work_form.csrf_token(),
                    row(
                        {"class": "mb-3"},
                        [
                            col({}, [form_control(work_form.type)]),
                            col({}, [form_control(work_form.shelf)]),
                        ],
                    ),
                    section_header("Details", "These details will overwrite any details provided by remote data"),
                    row(
                        {"class": "mb-3"},
                        [
                            col({}, [form_control(work_form.title)]),
                        ],
                    ),
                    row(
                        {"class": "mb-3"},
                        [
                            col({}, [form_control(work_form.author)]),
                            col({}, [form_control(work_form.series)]),
                            col({}, [form_control(work_form.release_date)]),
                        ],
                    ),
                    row(
                        {"class": "mb-3"},
                        [
                            col({}, [form_control(work_form.description, placeholder=details.description or "")]),
                        ],
                    ),
                    row(
                        {"class": "mb-3"},
                        [
                            col({}, [form_control(work_form.cover, placeholder=details.cover or "")]),
                            col({}, [form_control(work_form.background, placeholder=details.background or "")]),
                            col({}, [form_control(work_form.external_url, placeholder=details.external_url or "")]),
                        ],
                    ),
                    row({}, [col({}, [form_control(work_form.isbn)])]),
                ],
            ),
        ],
        title=page_title,
    )


def work_shelf_form_group(work: Work, work_shelf_form: WorkShelfForm) -> Heavymetal:
    action = flask.url_for("work.shelve", work_id=work.id)
    return form(
        {
            "class": "input-group",
            "method": "post",
            "action": action,
            "hx-post": action,
            "hx-trigger": "input changed from:find select throttle:1000ms",
        },
        [
            form_control(
                work_shelf_form.shelf,
                label=False,
                validation=False,
                data_loading_disable=True,
            ),
            work_shelf_form.csrf_token,
            button(
                {
                    "class": "btn btn-primary",
                    "type": "submit",
                    "data-loading-disable": True,
                },
                ["Change shelf"],
            ),
        ],
    )


def work_detail_page(work: Work, work_shelf_form: WorkShelfForm) -> Heavymetal:
    details = work.resolve_details()

    title = work.resolve_title()
    subtitle = f"{maybe_year(details.release_date)}, {maybe_str(details.author)}"

    work_details_panel = WorkDetailsPanel(work)
    work_records_panel = WorkRecordsPanel(work)

    external_data_subtitle = f"Details sourced from {html.count_plural('remote', len(work.remotes))}"
    if work.into_details():
        external_data_subtitle += " and manually entered metadata"

    return page(
        [
            section(
                {},
                [
                    page_header(title, subtitle, work_shelf_form_group(work, work_shelf_form)),
                    row({}, [col({}, [work_details_panel]), col({}, [work_records_panel])]),
                ],
            ),
            section(
                {},
                [
                    section_header("External data", external_data_subtitle),
                    row({"class": "row-cols-2 g-4"}, [col({}, [RemoteDetailsPanel(r)]) for r in work.iter_remotes()]),
                ],
            ),
            section(
                {},
                [
                    section_header("Search external sources", f"Search external sources for {quote_str(details.title)}"),
                    row({}, [col({}, [_search_for_work(work)])]),
                ],
            ),
        ],
        title=[maybe_str(details.title)],
    )


def work_update_page(work: Work, work_form: WorkForm) -> Heavymetal:
    title = work.resolve_title()

    if work.deleted:
        controls = btn_group([
            button(
                {
                    "class": "btn btn-outline-danger",
                    "type": "submit",
                    "formmethod": "post",
                    "formaction": work.url_for_permanently_delete(),
                    "title": "Delete this work. It will not be possible to recover.",
                },
                ["Permanently delete"],
            ),
            button(
                {
                    "class": "btn btn-outline-success",
                    "type": "submit",
                    "formmethod": "post",
                    "formaction": work.url_for_restore(),
                    "title": "Restore this work.",
                },
                ["Restore"],
            ),
        ])
    else:
        controls = btn_group([
            button(
                {
                    "class": "btn btn-outline-primary",
                    "type": "submit",
                    "formmethod": "post",
                    "formaction": work.url_for_delete(),
                    "title": "Delete this work. You will be able to restore it.",
                },
                ["Delete"],
            )
        ])

    return _work_form_page(
        work_form=work_form,
        title="Edit work",
        subtitle=return_to_work(work),
        page_title=[title, "Edit work"],
        details=EMPTY_DETAILS,
        action=work.url_for_update(),
        btn_groups=[controls],
    )


def work_create_page(work_form: WorkForm, details: Details = EMPTY_DETAILS) -> Heavymetal:
    return _work_form_page(
        work_form=work_form,
        details=details,
        title="Create work",
        subtitle="Manually enter details for a new work",
        action=flask.url_for("work.create"),
        btn_groups=[],
        page_title=["Create work"],
    )


def work_index_page(works: Pagination[Work], works_index_form: WorkIndexArgs) -> Heavymetal:
    works_table = generate_table_from_pagination(
        classes="table table-hover table-sm align-middle",
        cols=[
            {"style": "width: 10%;"},
            {"style": "width: 70%;"},
            {"style": "width: 20%;"},
        ],
        head=[
            th({}, ["Type"]),
            th({}, ["Title"]),
            th({}, ["Remote"]),
        ],
        body=lambda work: [
            td({}, [work.info.noun_title]),
            td({}, [details_description(work.resolve_details(), work.url_for())]),
            td(
                {"class": "text-body-secondary"},
                [
                    html.count_plural("remote", len(work.remotes)),
                    ", ",
                    html.count_plural("record", len(work.records)),
                ],
            ),
        ],
        pagination=works,
    )

    return page(
        [
            page_header("Works"),
            works_table,
        ],
        fluid=False,
        title=["Remotes"],
    )
