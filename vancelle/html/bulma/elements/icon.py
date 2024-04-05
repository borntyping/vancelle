from vancelle.html.document import element, span
from vancelle.html.helpers import html_classes, HtmlClasses
from vancelle.html.types import Hotmetal


def ion_icon(name: str) -> Hotmetal:
    return element("ion-icon", {"name": name}, [])


def icon(name: str, *classes: HtmlClasses) -> Hotmetal:
    return span({"class": html_classes("icon", classes)}, [ion_icon(name)])
