import dataclasses

from vancelle.html.bootstrap.layout.grid import col, row
from vancelle.html.bootstrap_icons import bi
from vancelle.html.vancelle.components.details import DetailsControl, DetailsPanel
from vancelle.html.vancelle.components.header import page_header
from vancelle.html.vancelle.components.optional import maybe_string
from vancelle.html.vancelle.pages.base import page
from vancelle.lib.heavymetal import Heavymetal, HeavymetalComponent
from vancelle.lib.heavymetal.html import a, div
from vancelle.models import Work


@dataclasses.dataclass()
class LibraryCard(HeavymetalComponent):
    work: Work

    def heavymetal(self) -> Heavymetal:
        return div({}, [])


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
                DetailsControl(name="Permalink", icon="file-earmark-fill", href=self.work.url_for()),
            ],
        )
        card = LibraryCard(work=self.work)

        return page(
            [
                page_header(title=panel.title(), subtitle=panel.date_and_author()),
                row({}, [col({}, [panel]), col({}, [card])]),
            ],
            title=[maybe_string(details.title)],
        )
