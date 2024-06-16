import dataclasses
import json
import typing

from vancelle.lib.heavymetal import Heavymetal, HeavymetalComponent
from vancelle.lib.heavymetal.html import code, div, p, pre


@dataclasses.dataclass()
class DetailsDescription(HeavymetalComponent):
    lines: typing.Sequence[str]

    def __init__(self, description: str | None):
        self.lines = description.splitlines() if description else []

    def __bool__(self) -> bool:
        return bool(self.lines)

    def heavymetal(self) -> Heavymetal:
        return div({"class": "text-body-secondary"}, [p({}, (line,)) for line in self.lines])


@dataclasses.dataclass()
class DetailsJSON(HeavymetalComponent):
    data: typing.Any

    def __bool__(self) -> bool:
        return bool(self.data)

    def heavymetal(self) -> Heavymetal:
        indent = None if isinstance(self.data, dict) and len(self.data) <= 1 else 2
        data = json.dumps(self.data, indent=indent)
        return div({"class": "p-2"}, [pre({"class": "bg-body-tertiary rounded p-2"}, [code({}, [data])])])
