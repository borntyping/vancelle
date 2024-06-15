from vancelle.lib.heavymetal import Heavymetal, HeavymetalContent
from vancelle.lib.heavymetal.html import div


def box(*children: HeavymetalContent) -> Heavymetal:
    return div({"class": "box"}, children=children)
