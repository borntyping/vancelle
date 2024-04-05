from vancelle.html.document import span
from vancelle.html.helpers import HtmlClasses, html_classes
from vancelle.html.hotmetal import Hotmetal


def ion_icon(name: str) -> Hotmetal:
    return ("ion-icon", {"name": name}, [])


def icon(name: str, *classes: HtmlClasses) -> Hotmetal:
    return span({"class": html_classes("icon", classes)}, [ion_icon(name)])
