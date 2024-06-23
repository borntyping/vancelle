import dataclasses
import typing

from vancelle.lib.html import html_classes, html_attrs
from vancelle.lib.heavymetal import Heavymetal, HeavymetalAttrs, HeavymetalComponent
from vancelle.lib.heavymetal.html import a, li, ul


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
    attrs: HeavymetalAttrs
    items: typing.Sequence[PageItem]

    def heavymetal(self) -> Heavymetal:
        return ul(html_attrs({"class": "pagination"}, self.attrs), self.items)
