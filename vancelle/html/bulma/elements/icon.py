from vancelle.html.document import element, span
from vancelle.html.types import Hotmetal


def icon(name: str) -> Hotmetal:
    return span({"class": "icon"}, [element("ion-icon", {"name": name}, [])])
