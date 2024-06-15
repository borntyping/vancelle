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
from vancelle.lib.heavymetal import Heavymetal, HeavymetalComponent, HeavymetalDynamicContent
from vancelle.lib.heavymetal.html import a, div, fragment, nav


@dataclasses.dataclass
class Tab:
    slug: str
    name: str
    content: HeavymetalDynamicContent = dataclasses.field(default=(), repr=False)
    classes: HtmlClasses = dataclasses.field(default=(), repr=False)

    def __bool__(self) -> bool:
        return any(self.content)

    @property
    def nav_id(self) -> str:
        return f"tab-{self.slug}"

    @property
    def pane_id(self) -> str:
        return f"tab-pane-{self.slug}"


@dataclasses.dataclass
class Tabs(HeavymetalComponent):
    id: str
    tabs: typing.Sequence[Tab] = dataclasses.field(repr=False)
    align_tabs: typing.Literal["left", "center", "right"] = "left"
    active_tab: int = 0

    def _nav_id(self, tab: Tab) -> str:
        return f"tab-{self.id}-{tab.slug}"

    def _pane_id(self, tab: Tab) -> str:
        return f"tab-pane-{self.id}-{tab.slug}"

    def heavymetal(self) -> Heavymetal:
        return fragment([self.navigation(), self.content()])

    def navigation(self) -> Heavymetal:
        return nav(
            {
                "class": html_classes(
                    "nav nav-tabs px-3",
                    {
                        "justify-content-start": self.align_tabs == "left",
                        "justify-content-center": self.align_tabs == "center",
                        "justify-content-end": self.align_tabs == "right",
                    },
                ),
                "id": self.id,
                "role": "tablist",
            },
            [
                a(
                    {
                        "class": html_classes("nav-link", {"active": index == self.active_tab}),
                        "id": self._nav_id(tab),
                        "data-bs-toggle": "tab",
                        "data-bs-target": "#" + self._pane_id(tab),
                        "type": "button",
                        "role": "tab",
                        "aria-controls": self._pane_id(tab),
                        "aria-selected": "true" if index == self.active_tab else "false",
                    },
                    [tab.name],
                )
                for index, tab in enumerate(self.tabs)
                if tab
            ],
        )

    def content(self) -> Heavymetal:
        return div(
            {"class": "tab-content v-tab-content"},
            [
                div(
                    {
                        "class": html_classes("tab-pane", {"show active": index == self.active_tab}, tab.classes),
                        "id": self._pane_id(tab),
                        "role": "tabpanel",
                        "aria-labelledby": self._nav_id(tab),
                        "tabindex": "0",
                    },
                    tab.content,
                )
                for index, tab in enumerate(self.tabs)
                if tab
            ],
        )
