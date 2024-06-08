"""
<ul class="nav nav-tabs" id="myTab" role="tablist">
  <li class="nav-item" role="presentation">
    <button class="nav-link active" id="home-tab" data-bs-toggle="tab" data-bs-target="#home-tab-pane" type="button" role="tab" aria-controls="home-tab-pane" aria-selected="true">Home</button>
  </li>
  <li class="nav-item" role="presentation">
    <button class="nav-link" id="profile-tab" data-bs-toggle="tab" data-bs-target="#profile-tab-pane" type="button" role="tab" aria-controls="profile-tab-pane" aria-selected="false">Profile</button>
  </li>
  <li class="nav-item" role="presentation">
    <button class="nav-link" id="contact-tab" data-bs-toggle="tab" data-bs-target="#contact-tab-pane" type="button" role="tab" aria-controls="contact-tab-pane" aria-selected="false">Contact</button>
  </li>
  <li class="nav-item" role="presentation">
    <button class="nav-link" id="disabled-tab" data-bs-toggle="tab" data-bs-target="#disabled-tab-pane" type="button" role="tab" aria-controls="disabled-tab-pane" aria-selected="false" disabled>Disabled</button>
  </li>
</ul>
<div class="tab-content" id="myTabContent">
  <div class="tab-pane fade show active" id="home-tab-pane" role="tabpanel" aria-labelledby="home-tab" tabindex="0">...</div>
  <div class="tab-pane fade" id="profile-tab-pane" role="tabpanel" aria-labelledby="profile-tab" tabindex="0">...</div>
  <div class="tab-pane fade" id="contact-tab-pane" role="tabpanel" aria-labelledby="contact-tab" tabindex="0">...</div>
  <div class="tab-pane fade" id="disabled-tab-pane" role="tabpanel" aria-labelledby="disabled-tab" tabindex="0">...</div>
</div>

"""

import dataclasses
import typing

from vancelle.html.helpers import HtmlClasses, html_classes
from vancelle.lib.heavymetal import Heavymetal, HeavymetalComponent, HeavymetalContent
from vancelle.lib.heavymetal.html import a, button, div, fragment, li, nav, ul


@dataclasses.dataclass
class Tab:
    slug: str
    name: str
    content: HeavymetalContent = ()

    @property
    def nav_id(self) -> str:
        return f"tab-{self.slug}"

    @property
    def pane_id(self) -> str:
        return f"tab-pane-{self.slug}"


@dataclasses.dataclass
class Tabs(HeavymetalComponent):
    id: str
    tabs: typing.Sequence[Tab]
    pane_classes: HtmlClasses = ()
    align_tabs: typing.Literal["left", "center", "right"] = "left"

    def nav_id(self, tab: Tab) -> str:
        return f"tab-{self.id}-{tab.slug}"

    def pane_id(self, tab: Tab) -> str:
        return f"tab-pane-{self.id}-{tab.slug}"

    def heavymetal(self) -> Heavymetal:
        nav_tabs = nav(
            {
                "class": html_classes(
                    "nav nav-tabs",
                    {
                        "justify-content-left": self.align_tabs == "left",
                        "justify-content-center": self.align_tabs == "center",
                        "justify-content-right": self.align_tabs == "right",
                    },
                ),
                "id": self.id,
                "role": "tablist",
            },
            [
                a(
                    {
                        "class": html_classes("nav-link", {"active": index == 0}),
                        "id": self.nav_id(tab),
                        "data-bs-toggle": "tab",
                        "data-bs-target": "#" + self.pane_id(tab),
                        "type": "button",
                        "role": "tab",
                        "aria-controls": self.pane_id(tab),
                        "aria-selected": "true" if index == 0 else "false",
                    },
                    [tab.name],
                )
                for index, tab in enumerate(self.tabs)
            ],
        )
        tab_content = div(
            {"class": "tab-content"},
            [
                div(
                    {
                        "class": html_classes("tab-pane", {"show active": index == 0}, self.pane_classes),
                        "id": self.pane_id(tab),
                        "role": "tabpanel",
                        "aria-labelledby": self.nav_id(tab),
                        "tabindex": "0",
                    },
                    tab.content,
                )
                for index, tab in enumerate(self.tabs)
            ],
        )
        return fragment([nav_tabs, tab_content])
