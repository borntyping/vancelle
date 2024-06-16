import dataclasses

import flask

from vancelle.extensions import html
from vancelle.html.bootstrap.layout.grid import col, row
from vancelle.html.vancelle.components.header import page_header, section_header
from vancelle.html.vancelle.components.panel import RemoteDetailsPanel, WorkDetailsPanel, WorkRecordsPanel
from vancelle.html.vancelle.components.optional import maybe_str, maybe_year, quote
from vancelle.html.vancelle.pages.base import page
from vancelle.lib.heavymetal import Heavymetal, HeavymetalComponent
from vancelle.lib.heavymetal.html import a, div, section
from vancelle.models import Remote, Work


def search_for_work(work: Work) -> Heavymetal:
    subclasses = Remote.filter_subclasses(can_search=True)
    return div(
        {"class": "list-group"},
        [
            a(
                {
                    "class": "list-group-item list-group-item-action",
                    "href": flask.url_for(
                        "remote.search_source",
                        remote_type=cls.remote_type(),
                        work_id=work.id,
                    ),
                },
                ["Search ", cls.info.noun_full_plural],
            )
            for cls in subclasses
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
                        row({"class": "row-cols-2"}, [col({}, [RemoteDetailsPanel(r)]) for r in self.work.remotes]),
                    ],
                ),
                section(
                    {},
                    [
                        section_header(
                            title="Search external sources",
                            subtitle=f"Search external sources for {quote(details.title)}",
                        ),
                        row({}, [col({}, [search_for_work(self.work)])]),
                    ],
                ),
            ],
            title=[maybe_str(details.title)],
        )
