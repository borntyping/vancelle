import dataclasses

from flask import url_for

from vancelle.html.bootstrap.layout.grid import col, row
from vancelle.html.vancelle.components.details import DetailsPanel, PanelControl
from vancelle.html.vancelle.components.header import page_header
from vancelle.html.vancelle.components.librarycard import LibraryCard
from vancelle.html.vancelle.components.optional import maybe_string
from vancelle.html.vancelle.pages.base import page
from vancelle.lib.heavymetal import Heavymetal, HeavymetalComponent
from vancelle.models import Work


@dataclasses.dataclass()
class WorkPage(HeavymetalComponent):
    work: Work

    def heavymetal(self) -> Heavymetal:
        details = self.work.resolve_details()
        properties = list(self.work.into_properties())

        panel = DetailsPanel(
            details=details,
            properties=properties,
            controls=[
                PanelControl(name="Edit", icon="pencil", href=url_for("work.update", work_id=self.work.id)),
            ],
        )
        card = LibraryCard(work=self.work, details=details)

        return page(
            [
                page_header(title=panel.title(), subtitle=panel.date_and_author()),
                row({}, [col({}, [panel]), col({}, [card])]),
            ],
            title=[maybe_string(details.title)],
        )
