import dataclasses

import flask

from vancelle.extensions import html
from vancelle.forms.work import WorkForm
from vancelle.html.bootstrap.forms.controls import form_control
from vancelle.html.bootstrap.layout.grid import col, row
from vancelle.html.vancelle.components.header import page_header, section_header
from vancelle.html.vancelle.components.panel import RemoteDetailsPanel, WorkDetailsPanel, WorkRecordsPanel
from vancelle.html.vancelle.components.optional import maybe_str, maybe_year, quote_str
from vancelle.html.vancelle.pages.base import page
from vancelle.lib.heavymetal import Heavymetal, HeavymetalComponent
from vancelle.lib.heavymetal.html import a, button, div, form, section
from vancelle.models import Remote, Work
from vancelle.models.details import Details, EMPTY_DETAILS


def search_for_work(work: Work) -> Heavymetal:
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


@dataclasses.dataclass()
class WorkPage(HeavymetalComponent):
    work: Work

    def heavymetal(self) -> Heavymetal:
        details = self.work.resolve_details()

        work_details_panel = WorkDetailsPanel(self.work)
        work_records_panel = WorkRecordsPanel(self.work)

        external_data_subtitle = f"Details sourced from {html.count_plural('remote', len(self.work.remotes))}"
        if self.work.into_details():
            external_data_subtitle += " and manually entered metadata"

        return page(
            [
                section(
                    {},
                    [
                        page_header(
                            title=maybe_str(details.title),
                            subtitle=f"{maybe_year(details.release_date)}, {maybe_str(details.author)}",
                        ),
                        row({}, [col({}, [work_details_panel]), col({}, [work_records_panel])]),
                    ],
                ),
                section(
                    {},
                    [
                        section_header(
                            title="External data",
                            subtitle=external_data_subtitle,
                        ),
                        row({"class": "row-cols-2 g-4"}, [col({}, [RemoteDetailsPanel(r)]) for r in self.work.remotes]),
                    ],
                ),
                section(
                    {},
                    [
                        section_header(
                            title="Search external sources",
                            subtitle=f"Search external sources for {quote_str(details.title)}",
                        ),
                        row({}, [col({}, [search_for_work(self.work)])]),
                    ],
                ),
            ],
            title=[maybe_str(details.title)],
        )


def create_work_page(work_form: WorkForm, details: Details = EMPTY_DETAILS) -> Heavymetal:
    return page(
        [
            form(
                {"id": "create-work", "method": "post", "action": ""},
                [
                    page_header(
                        "Create work",
                        "Manually enter details for a new work",
                        [button({"class": "btn btn-lg btn-primary", "type": "submit"}, ["Save"])],
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
        title=["Create work"],
    )
