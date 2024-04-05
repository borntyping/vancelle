from vancelle.html.document import div
from vancelle.html.hotmetal import Hotmetal


def columns(*children: Hotmetal) -> Hotmetal:
    return div({"class": "columns"}, [div({"class": "column"}, [c]) for c in children])
