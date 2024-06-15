from vancelle.lib.heavymetal import Heavymetal, HeavymetalDynamicContent
from vancelle.lib.heavymetal.html import div


def box(*children: HeavymetalDynamicContent) -> Heavymetal:
    return div({"class": "box"}, children=children)
