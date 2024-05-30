from vancelle.lib.heavymetal import Heavymetal, HeavymetalChildren
from vancelle.lib.heavymetal.html import div


def box(*children: HeavymetalChildren) -> Heavymetal:
    return div({"class": "box"}, children=children)
