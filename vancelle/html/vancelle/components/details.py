import dataclasses
import textwrap
import typing

from vancelle.html.bootstrap.components.tabs import Tab, Tabs
from vancelle.html.bootstrap.utilities.background import BackgroundColour
from vancelle.html.bootstrap_icons import bi
from vancelle.html.vancelle.components.optional import ABSENT, maybe_string
from vancelle.lib.heavymetal import Heavymetal, HeavymetalComponent, HeavymetalTuple
from vancelle.lib.heavymetal.html import a, div, figure, fragment, h3, img, nothing, p, span
from vancelle.models.details import Details
from vancelle.models.properties import Property


@dataclasses.dataclass(kw_only=True)
class DetailsControl(HeavymetalComponent):
    name: str
    href: str
    icon: str
    colour: BackgroundColour = "primary"

    def heavymetal(self) -> Heavymetal:
        return a({"class": f"btn btn-sm btn-{self.colour}", "title": self.name}, [bi(self.icon)])


@dataclasses.dataclass(kw_only=True)
class DetailsPanel(HeavymetalComponent):
    details: Details
    background_colour: BackgroundColour = "primary"
    controls: typing.Sequence[DetailsControl] = ()
    data: str | None = None
    properties: typing.Sequence[Property] = ()

    def title(self, *, href: str | None = None) -> Heavymetal:
        title = maybe_string(self.details.title)
        return a({"href": href}, [title]) if href else span({}, [title])

    def date_and_author(self) -> Heavymetal:
        year = str(self.details.release_date.year) if self.details.release_date else ABSENT
        author = textwrap.shorten(self.details.author, 50) if self.details.author else ABSENT

        return fragment(
            [
                span({"title": maybe_string(self.details.release_date)}, [year]),
                ", ",
                span({"title": maybe_string(self.details.author)}, [author]),
            ]
        )

    def description(self) -> Heavymetal:
        if not self.details.description:
            return nothing()

        return [p({}, (line,)) for line in self.details.description.splitlines()]

    def tags(self) -> Heavymetal:
        return fragment([])

    def external_url(self) -> Heavymetal:
        return fragment([])

    def heavymetal(self) -> Heavymetal:
        tabs = Tabs(
            id="remote",
            tabs=[
                Tab("description", "Description", self.description()),
                Tab("details", "Details", [p({}, ["...Details..."])]),
                Tab("properties", "Properties", [p({}, ["...Properties..."])]),
                Tab("data", "Data", [p({}, ["...Data..."])]),
            ],
            pane_classes="p-3",
            align_tabs="center",
        )

        background = f"background-image: url('{self.details.background}');" if self.details.background else ""

        return div(
            {"class": "v-panel border rounded"},
            [
                div(
                    {"class": f"v-panel-header p-1 text-end bg-{self.background_colour}-subtle", "style": background},
                    self.controls,
                ),
                figure(
                    {"class": f"v-panel-cover bg-{self.background_colour}"},
                    [
                        (
                            img(
                                {
                                    "class": "fs-7",
                                    "src": self.details.cover,
                                    "alt": f"Cover for {self.details.title}.",
                                    "loading": "lazy",
                                }
                            )
                            if self.details.cover
                            else nothing()
                        )
                    ],
                ),
                div(
                    {"class": "v-panel-body"},
                    [
                        h3({"class": "card-title mb-1"}, [self.details.title]),
                        self.date_and_author(),
                        self.tags(),
                        self.external_url(),
                        p({}, [f"{self.background_colour=}"]),
                    ],
                ),
                div({"class": "v-panel-tabs mt-3"}, [tabs]),
            ],
        )
