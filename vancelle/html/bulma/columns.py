from vancelle.lib.heavymetal.html import div
from vancelle.lib.heavymetal import Heavymetal


def columns(*children: Heavymetal) -> Heavymetal:
    return div({"class": "columns "}, [div({"class": "column"}, [c]) for c in children])
