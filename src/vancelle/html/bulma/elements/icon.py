from vancelle.lib.heavymetal.html import span
from vancelle.lib.html import HtmlClasses, html_classes
from vancelle.lib.heavymetal import Heavymetal


def ion_icon(name: str) -> Heavymetal:
    return ("ion-icon", {"name": name}, [])


def icon(name: str, *classes: HtmlClasses) -> Heavymetal:
    return span({"class": html_classes("icon", classes)}, [ion_icon(name)])
