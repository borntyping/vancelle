from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import title


def vancelle_title(*parts: str) -> Heavymetal:
    name = " - ".join(["Vancelle", *parts])
    return title({}, [name])
