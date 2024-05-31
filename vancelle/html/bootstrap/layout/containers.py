from vancelle.lib.heavymetal import Heavymetal, HeavymetalContent
from vancelle.lib.heavymetal.html import div


def container(content: HeavymetalContent) -> Heavymetal:
    return div({"class": "container"}, content)
