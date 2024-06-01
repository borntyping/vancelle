import dataclasses
import typing

from vancelle.html.helpers import HtmlClasses, html_classes
from vancelle.lib.heavymetal import Heavymetal, HeavymetalComponent
from vancelle.lib.heavymetal.html import a, li, nav, ul


@dataclasses.dataclass
class PageItem(HeavymetalComponent):
    text: str
    href: str | None
    active: bool = False

    def heavymetal(self) -> Heavymetal:
        classes = {"page-link": True, "disabled": not self.href, "active": self.active}
        return li({"class": "page-item"}, [a({"class": html_classes(classes), "href": self.href}, [self.text])])


@dataclasses.dataclass
class Pagination(HeavymetalComponent):
    items: typing.Sequence[PageItem]
    center: bool = False
    classes: HtmlClasses = ()

    def heavymetal(self) -> Heavymetal:
        return ul({"class": html_classes("pagination", {"justify-content-center": self.center}, self.classes)}, self.items)
