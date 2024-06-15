import dataclasses
import json
import textwrap
import typing

import markupsafe

from vancelle.html.bootstrap.components.tabs import Tab, Tabs
from vancelle.html.bootstrap.utilities.background import BackgroundColour
from vancelle.html.bootstrap_icons import bi_font
from vancelle.html.vancelle.components.optional import ABSENT, maybe_string
from vancelle.lib.heavymetal import Heavymetal, HeavymetalComponent
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
    pre,
    span,
    table,
    tbody,
    td,
    th,
    tr,
)
from vancelle.models.details import Details
from vancelle.models.properties import Property


@dataclasses.dataclass()
class Properties(HeavymetalComponent):
    properties: typing.Sequence[Property]

    def heavymetal(self) -> Heavymetal:
        return table(
            {"class": "table"},
            [
                tbody(
                    {},
                    [
                        tr(
                            {},
                            [
                                th({"scope": "row"}, [prop.name]),
                                td({}, [prop]),
                            ],
                        )
                        for prop in self.properties
                        if prop
                    ],
                )
            ],
        )


@dataclasses.dataclass()
class DetailsDescription(HeavymetalComponent):
    lines: typing.Sequence[str]

    def __init__(self, description: str | None):
        self.lines = description.splitlines() if description else []

    def __bool__(self) -> bool:
        return bool(self.lines)

    def heavymetal(self) -> Heavymetal:
        return div({"class": "text-body-secondary"}, [p({}, (line,)) for line in self.lines])


@dataclasses.dataclass()
class DetailsJSON(HeavymetalComponent):
    data: typing.Any

    def __bool__(self) -> bool:
        return bool(self.data)

    def heavymetal(self) -> Heavymetal:
        data = markupsafe.Markup(json.dumps(self.data, indent=2))
        return pre({}, [code({}, [data])])


@dataclasses.dataclass(kw_only=True)
class PanelControl(HeavymetalComponent):
    name: str
    href: str
    icon: str

    def heavymetal(self) -> Heavymetal:
        return a({"class": "btn btn-sm btn-outline-light", "title": self.name}, [bi_font(self.icon)])


@dataclasses.dataclass(kw_only=True)
class Panel(HeavymetalComponent):
    details: Details

    def header_style(self) -> str | None:
        if not self.details.background:
            return None

        return f"background-image: url('{self.details.background}');"

    def header(self, controls: typing.Sequence[PanelControl], title: str | None = None) -> Heavymetal:
        return div(
            {"class": "v-panel-header p-1 text-end bg-primary", "style": self.header_style()},
            [title if title else nothing(), *controls],
        )


@dataclasses.dataclass(kw_only=True)
class DetailsPanel(Panel, HeavymetalComponent):
    data: str | None = dataclasses.field(default=None, repr=False)
    background_colour: BackgroundColour = "primary"

    properties: typing.Sequence[Property] = dataclasses.field(default_factory=tuple, repr=False)
    controls: typing.Sequence[PanelControl] = dataclasses.field(default_factory=tuple, repr=False)

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

    def tags(self) -> Heavymetal:
        return fragment([])

    def external_url(self) -> Heavymetal:
        return fragment([])

    def heavymetal(self) -> Heavymetal:
        tabs = Tabs(
            id="remote",
            tabs=[
                Tab("description", "Description", [DetailsDescription(self.details.description)], classes="p-3"),
                Tab("details", "Details", [Properties(list(self.details.into_properties()))]),
                Tab("properties", "Properties", [Properties(list(self.properties))]),
                Tab("data", "Data", [DetailsJSON(self.data)], classes="p-3"),
            ],
            align_tabs="right",
            active_tab=1,
        )

        return div(
            {"class": "v-panel v-panel-details border rounded overflow-hidden"},
            [
                div(
                    {"class": "v-panel-header p-1 text-end bg-primary", "style": self.header_style()},
                    self.controls,
                ),
                div(
                    {"class": "v-panel-cover border-bottom p-3 pe-0"},
                    [
                        figure(
                            {"class": f"m-0 rounded-3 bg-{self.background_colour}"},
                            [
                                (
                                    img(
                                        {
                                            "class": "rounded-3 fs-7",
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
                div({"class": "v-panel-tabs-nav"}, [tabs.navigation()]),
                div({"class": "v-panel-tabs-content"}, [tabs.content()]),
            ],
        )
